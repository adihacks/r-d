import pandas as pd
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.parse
import warnings
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Suppress SSL warnings
warnings.filterwarnings('ignore', category=requests.packages.urllib3.exceptions.InsecureRequestWarning)

# Configuration
MAX_WORKERS = 15
TIMEOUT = 25
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'DNT': '1'
}

def requests_retry_session():
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def enhanced_form_detection(soup, url):
    """Comprehensive form detection with multiple strategies"""
    # Strategy 1: Direct password field detection
    password_fields = soup.find_all('input', {'type': 'password'})
    for field in password_fields:
        form = field.find_parent('form')
        if form:
            return form, 'password_field'

    # Strategy 2: Common login patterns in form attributes
    login_indicators = ['login', 'signin', 'auth', 'authenticate', 'account']
    for form in soup.find_all('form'):
        form_id = form.get('id', '').lower()
        form_class = form.get('class', [])
        form_action = form.get('action', '').lower()
        
        if any(indicator in form_id for indicator in login_indicators) or \
           any(indicator in ' '.join(form_class) for indicator in login_indicators) or \
           any(indicator in form_action for indicator in login_indicators):
            return form, 'form_attributes'

    # Strategy 3: Social login detection
    sso_indicators = ['sso', 'oauth', 'social', 'google', 'facebook', 'apple']
    sso_links = soup.find_all('a', href=lambda x: x and any(kw in x.lower() for kw in sso_indicators))
    if sso_links:
        return None, 'sso_required'

    # Strategy 4: Phone number detection
    phone_fields = soup.find_all('input', {'type': 'tel'})
    if phone_fields:
        return None, 'phone_required'

    # Strategy 5: Generic form analysis
    for form in soup.find_all('form'):
        inputs = form.find_all('input')
        if len(inputs) >= 2:  # At least username/password fields
            text_fields = [inp for inp in inputs if inp.get('type') in ['text', 'email']]
            if text_fields and password_fields:
                return form, 'generic_form'

    return None, 'no_form_detected'


def enhanced_liveness_check(url):
    try:
        with requests_retry_session() as s:
            resp = s.get(
                url,
                headers=HEADERS,
                timeout=TIMEOUT,
                allow_redirects=True,
                verify=False,
                stream=True
            )
            return url if 100 <= resp.status_code < 500 else None
    except Exception:
        return None

def comprehensive_login_check(row):
    result = {
        'S.No': row['S.No'],
        'URL': row['URL'],
        'Status': 'pending',
        'Details': ''
    }
    
    try:
        with requests_retry_session() as s:
            s.headers.update(HEADERS)
            
            # Initial request
            resp = s.get(row['URL'], timeout=TIMEOUT, verify=False)
            
            if resp.status_code != 200:
                result['Status'] = 'error'
                result['Details'] = f'HTTP {resp.status_code}'
                return result
                
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # CAPTCHA detection
            captcha_elements = soup.find_all(
                lambda tag: 'captcha' in tag.get('id', '').lower() or 
                'captcha' in ' '.join(tag.get('class', []))
            )
            if captcha_elements:
                result['Status'] = 'captcha'
                result['Details'] = 'CAPTCHA detected'
                return result
                
            # Enhanced form detection
            form, detection_method = enhanced_form_detection(soup, row['URL'])
            
            if not form:
                if detection_method == 'sso_required':
                    result['Status'] = 'error'
                    result['Details'] = 'SSO authentication required'
                elif detection_method == 'phone_required':
                    result['Status'] = 'error'
                    result['Details'] = 'Phone number verification needed'
                else:
                    result['Status'] = 'error'
                    result['Details'] = 'No login form detected'
                return result
                
            # Form field analysis
            form_data = {}
            username_fields = ['email', 'username', 'userid', 'login', 'user', 'phone']
            password_fields = ['password', 'passwd', 'pwd', 'pass']
            
            inputs = form.find_all('input')
            username_field = next(
                (inp for inp in inputs 
                 if inp.get('type') in ['text', 'email', 'tel'] and 
                 any(f in inp.get('name', '').lower() for f in username_fields)),
                None
            )
            
            password_field = next(
                (inp for inp in inputs 
                 if inp.get('type') == 'password' or 
                 any(f in inp.get('name', '').lower() for f in password_fields)),
                None
            )
            
            if not username_field or not password_field:
                result['Status'] = 'error'
                result['Details'] = 'Could not find username/password fields'
                return result
                
            # Build form data
            for inp in inputs:
                name = inp.get('name')
                value = inp.get('value', '')
                inp_type = inp.get('type', '').lower()
                
                if inp_type == 'hidden':
                    form_data[name] = value
                elif inp == username_field:
                    form_data[name] = row['Username']
                elif inp == password_field:
                    form_data[name] = row['Password']
                    
            # Submit form
            action = form.get('action', row['URL'])
            target_url = urllib.parse.urljoin(row['URL'], action)
            method = form.get('method', 'post').lower()
            
            if method == 'post':
                login_resp = s.post(target_url, data=form_data, 
                                  timeout=TIMEOUT, verify=False)
            else:
                login_resp = s.get(target_url, params=form_data,
                                timeout=TIMEOUT, verify=False)
                
            # Comprehensive result analysis
            final_url = login_resp.url.lower()
            content = login_resp.text.lower()
            cookies = s.cookies.get_dict()
            
            # Failure indicators
            failure_keywords = [
                'invalid', 'incorrect', 'error', 'try again', 
                'wrong', 'not recognized', 'mismatch', 'unable to log in',
                'check your credentials', 'password you entered is incorrect'
            ]
            
            # Success indicators
            success_keywords = [
                'logout', 'sign out', 'my account', 'dashboard',
                'welcome', 'account details', 'profile', 'settings'
            ]
            
            # Session cookie detection
            session_cookies = ['session', 'auth', 'token', 'access', 'login']
            has_session = any(kw in cookie.lower() for cookie in cookies for kw in session_cookies)
            
            # URL pattern analysis
            success_urls = ['/home', '/dashboard', '/account']
            failure_urls = ['/login', '/signin', '/error']
            
            if any(kw in content for kw in failure_keywords) or \
               any(url in final_url for url in failure_urls):
                result['Status'] = 'fail'
                result['Details'] = 'Invalid credentials'
            elif has_session or \
                 any(kw in content for kw in success_keywords) or \
                 any(url in final_url for url in success_urls):
                result['Status'] = 'success'
                result['Details'] = 'Login successful'
            else:
                # Check for 2FA requirements
                if 'two-factor' in content or '2fa' in content or 'otp' in content:
                    result['Status'] = 'error'
                    result['Details'] = 'Two-factor authentication required'
                else:
                    result['Status'] = 'unknown'
                    result['Details'] = 'Inconclusive result'

    except Exception as e:
        result['Status'] = 'error'
        result['Details'] = f'Exception: {str(e)}'
        
    return result

def main():
    try:
        df = pd.read_excel('credentials.xlsx').convert_dtypes()
    except FileNotFoundError:
        print("Error: credentials.xlsx not found")
        return

    # Phase 1: Liveness check
    print("🔍 Checking live URLs...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(enhanced_liveness_check, row['URL']): row 
                 for _, row in df.iterrows()}
        live_data = []
        
        for future in as_completed(futures):
            url = future.result()
            row = futures[future]
            if url:
                live_data.append(row)
                print(f"✅ Live: {url}")

    live_df = pd.DataFrame(live_data)
    
    print("\n" + "="*60)
    print(f"🌐 Live URLs: {len(live_df)}/{len(df)}")
    print("="*60 + "\n")
    
    # Phase 2: Credential verification
    print("🔐 Verifying credentials...\n")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(comprehensive_login_check, row) 
                 for _, row in live_df.iterrows()]
        
        for future in as_completed(futures):
            result = future.result()
            status = result['Status'].lower()
            colors = {
                'success': '\033[92m',
                'fail': '\033[91m',
                'captcha': '\033[93m',
                'error': '\033[91m',
                'unknown': '\033[94m'
            }
            icons = {
                'success': '✔',
                'fail': '✖',
                'captcha': '⚠',
                'error': '❗',
                'unknown': '❓'
            }
            
            output = [
                f"{colors.get(status, '')}[{icons.get(status, ' ')}] S.No {result['S.No']} - {result['URL']}",
                f"   Status: {result['Status'].upper()} - {result['Details']}\033[0m"
            ]
            print('\n'.join(output))

if __name__ == "__main__":
    main()


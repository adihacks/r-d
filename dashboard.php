<?php
// config.php (secure credentials)
require_once 'config.php';

$conn = new mysqli("localhost", "telegram_user", "73033", "telegram_alerts");
if ($conn->connect_error) die("🔒 Connection Failed: ".$conn->connect_error);

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CYBER THREAT DASHBOARD</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --matrix-green: #00ff88;
            --neon-cyan: #00ffff;
            --hacker-bg: #001100;
        }

        body {
            background: #000;
            color: var(--matrix-green);
            font-family: 'Courier New', monospace;
        }

        .alert-card {
            background: #001100;
            border: 1px solid #00ff00;
            margin: 10px;
            padding: 15px;
            position: relative;
            transition: all 0.3s;
        }

        .alert-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 0 15px #00ff0055;
        }

        .source-link {
            color: #00ffff !important;
            text-decoration: none;
        }

        .source-link:hover {
            text-decoration: underline;
        }

        #statsPanel {
            border: 2px solid #00ff00;
            padding: 20px;
            margin: 15px;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <!-- Header -->
        <div class="row p-4 bg-dark">
            <div class="col-12 text-center">
                <h1 class="mb-3">🛡️ CYBER SECURITY ALERT CENTER</h1>
                <div id="statsPanel">
                    <div class="row">
                        <div class="col-md-4">📊 Total Alerts: <?= totalAlerts() ?></div>
                        <div class="col-md-4">🚨 Last 24h: <?= alertsLast24h() ?></div>
                        <div class="col-md-4">🔑 Top Keyword: <?= topKeyword() ?></div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Alerts Container -->
        <div class="row mt-4">
            <div class="col-12">
                <?php
                $result = $conn->query("
                    SELECT * 
                    FROM alerts 
                    ORDER BY timestamp DESC 
                    LIMIT 50
                ");
                
                while($row = $result->fetch_assoc()):
                ?>
                <div class="alert-card">
                    <div class="d-flex justify-content-between align-items-start">
                        <div style="width: 80%">
                            <h4>
                                <span class="badge bg-danger"><?= $row['matched_keywords'] ?></span>
                                Alert #<?= $row['id'] ?>
                            </h4>
                            <small class="text-muted"><?= $row['timestamp'] ?></small>
                            <div class="mt-2 message-text">
                                <?= nl2br(htmlspecialchars(substr($row['message_text'], 0, 500))) ?>
                                <?= (strlen($row['message_text']) > 500) ? '...' : '' ?>
                            </div>
                        </div>
                        <div class="text-end">
                            <a href="<?= $row['source_url'] ?>" 
                               class="btn btn-outline-warning source-link"
                               target="_blank">
                               🔗 Source
                            </a>
                        </div>
                    </div>
                </div>
                <?php endwhile; ?>
            </div>
        </div>
    </div>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
    // Auto-refresh every 5 seconds
    function updateDashboard() {
        $.ajax({
            url: window.location.href,
            success: function(data) {
                const newContent = $(data).find('.alert-card').first();
                if(!document.body.innerHTML.includes(newContent.html())) {
                    $('.alert-card:last').remove();
                    $('#statsPanel').html($(data).find('#statsPanel').html());
                    $('.col-12').prepend(newContent);
                }
            }
        });
    }
    setInterval(updateDashboard, 5000);
    </script>
</body>
</html>

<?php
// Helper functions
function totalAlerts() {
    global $conn;
    return $conn->query("SELECT COUNT(*) FROM alerts")->fetch_row()[0];
}

function alertsLast24h() {
    global $conn;
    return $conn->query("SELECT COUNT(*) FROM alerts 
                       WHERE timestamp > NOW() - INTERVAL 24 HOUR")->fetch_row()[0];
}

function topKeyword() {
    global $conn;
    $result = $conn->query("SELECT matched_keywords FROM alerts 
                          GROUP BY matched_keywords 
                          ORDER BY COUNT(*) DESC 
                          LIMIT 1");
    return $result->num_rows > 0 ? $result->fetch_row()[0] : 'N/A';
}
?>
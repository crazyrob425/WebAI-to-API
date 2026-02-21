#include "mainwindow.h"
#include <QCloseEvent>
#include <QHostAddress>
#include <QFile>
#include <QDir>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , m_serverRunning(false)
    , m_serverPort("6969")
{
    setupUi();
    setupTrayIcon();
    setupConnections();
    
    log("WebAI-to-API GUI Started");
    log("Ready to start the server...");
}

MainWindow::~MainWindow()
{
    if (serverProcess && serverProcess->state() == QProcess::Running) {
        serverProcess->terminate();
        serverProcess->waitForFinished(3000);
    }
}

void MainWindow::setupUi()
{
    setWindowTitle("WebAI-to-API");
    resize(800, 600);
    setMinimumSize(600, 400);

    centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);

    // Main layout
    QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);
    
    // Header
    QLabel *titleLabel = new QLabel("WebAI-to-API Desktop", this);
    titleLabel->setStyleSheet("font-size: 24px; font-weight: bold; color: #2a82da; padding: 10px;");
    titleLabel->setAlignment(Qt::AlignCenter);
    mainLayout->addWidget(titleLabel);
    
    // Status bar at top
    QHBoxLayout *statusLayout = new QHBoxLayout();
    
    statusLabel = new QLabel("Status: Ready", this);
    statusLabel->setStyleSheet("font-weight: bold; color: #888;");
    statusLayout->addWidget(statusLabel);
    
    statusLayout->addStretch();
    
    serverStatusLabel = new QLabel("Server: Stopped", this);
    serverStatusLabel->setStyleSheet("color: #ff6b6b; font-weight: bold;");
    statusLayout->addWidget(serverStatusLabel);
    
    mainLayout->addLayout(statusLayout);
    
    // Tab widget for different sections
    tabWidget = new QTabWidget(this);
    
    // ========== CONTROL TAB ==========
    QWidget *controlTab = new QWidget();
    QVBoxLayout *controlLayout = new QVBoxLayout(controlTab);
    
    // Server controls group
    QGroupBox *serverGroup = new QGroupBox("Server Control", this);
    QVBoxLayout *serverGroupLayout = new QVBoxLayout(serverGroup);
    
    QHBoxLayout *portLayout = new QHBoxLayout();
    portLayout->addWidget(new QLabel("Port:", this));
    portLineEdit = new QLineEdit(m_serverPort, this);
    portLineEdit->setPlaceholderText("6969");
    portLineEdit->setMaximumWidth(100);
    portLayout->addWidget(portLineEdit);
    portLayout->addStretch();
    serverGroupLayout->addLayout(portLayout);
    
    QHBoxLayout *buttonLayout = new QHBoxLayout();
    startStopButton = new QPushButton("Start Server", this);
    startStopButton->setStyleSheet("padding: 10px; font-weight: bold; background-color: #4CAF50; color: white; border: none;");
    startStopButton->setMinimumHeight(40);
    buttonLayout->addWidget(startStopButton);
    
    testApiButton = new QPushButton("Test API", this);
    testApiButton->setStyleSheet("padding: 10px; background-color: #2196F3; color: white; border: none;");
    testApiButton->setMinimumHeight(40);
    testApiButton->setEnabled(false);
    buttonLayout->addWidget(testApiButton);
    
    serverGroupLayout->addLayout(buttonLayout);
    controlLayout->addWidget(serverGroup);
    
    // Log output
    QGroupBox *logGroup = new QGroupBox("Server Log", this);
    QVBoxLayout *logGroupLayout = new QVBoxLayout(logGroup);
    
    logTextEdit = new QTextEdit(this);
    logTextEdit->setReadOnly(true);
    logTextEdit->setStyleSheet("background-color: #1e1e1e; color: #00ff00; font-family: monospace; font-size: 11px;");
    logTextEdit->setMaximumHeight(200);
    logGroupLayout->addWidget(logTextEdit);
    
    QPushButton *clearLogButton = new QPushButton("Clear Log", this);
    clearLogButton->setStyleSheet("padding: 5px;");
    logGroupLayout->addWidget(clearLogButton);
    connect(clearLogButton, &QPushButton::clicked, this, &MainWindow::clearLog);
    
    controlLayout->addWidget(logGroup);
    controlLayout->addStretch();
    
    tabWidget->addTab(controlTab, "Control");
    
    // ========== SETTINGS TAB ==========
    QWidget *settingsTab = new QWidget();
    QVBoxLayout *settingsLayout = new QVBoxLayout(settingsTab);
    
    // Browser settings
    QGroupBox *browserGroup = new QGroupBox("Browser Settings", this);
    QVBoxLayout *browserGroupLayout = new QVBoxLayout(browserGroup);
    
    QHBoxLayout *browserLayout = new QHBoxLayout();
    browserLayout->addWidget(new QLabel("Browser:", this));
    browserComboBox = new QComboBox(this);
    browserComboBox->addItems({"Firefox", "Chrome", "Brave", "Edge", "Safari", "Auto-detect"});
    browserLayout->addWidget(browserComboBox);
    browserLayout->addStretch();
    browserGroupLayout->addLayout(browserLayout);
    settingsLayout->addWidget(browserGroup);
    
    // Proxy settings
    QGroupBox *proxyGroup = new QGroupBox("Proxy Settings", this);
    QVBoxLayout *proxyGroupLayout = new QVBoxLayout(proxyGroup);
    
    QHBoxLayout *proxyLayout = new QHBoxLayout();
    proxyLayout->addWidget(new QLabel("HTTP Proxy:", this));
    proxyLineEdit = new QLineEdit(this);
    proxyLineEdit->setPlaceholderText("http://127.0.0.1:2334 (optional)");
    proxyLayout->addWidget(proxyLineEdit);
    proxyGroupLayout->addLayout(proxyLayout);
    settingsLayout->addWidget(proxyGroup);
    
    // Model settings
    QGroupBox *modelGroup = new QGroupBox("AI Model", this);
    QVBoxLayout *modelGroupLayout = new QVBoxLayout(modelGroup);
    
    QHBoxLayout *modelLayout = new QHBoxLayout();
    modelLayout->addWidget(new QLabel("Default Model:", this));
    modelComboBox = new QComboBox(this);
    modelComboBox->addItems({"gemini-2.5-flash", "gemini-2.5-pro", "gemini-3.0-pro"});
    modelLayout->addWidget(modelComboBox);
    modelLayout->addStretch();
    modelGroupLayout->addLayout(modelLayout);
    settingsLayout->addWidget(modelGroup);
    
    saveSettingsButton = new QPushButton("Save Settings", this);
    saveSettingsButton->setStyleSheet("padding: 10px; background-color: #FF9800; color: white; border: none;");
    saveSettingsButton->setMinimumHeight(40);
    settingsLayout->addWidget(saveSettingsButton);
    settingsLayout->addStretch();
    
    tabWidget->addTab(settingsTab, "Settings");
    
    // ========== TEST CHAT TAB ==========
    QWidget *chatTab = new QWidget();
    QVBoxLayout *chatLayout = new QVBoxLayout(chatTab);
    
    chatInputLineEdit = new QLineEdit(this);
    chatInputLineEdit->setPlaceholderText("Type your message here...");
    chatInputLineEdit->setEnabled(false);
    chatLayout->addWidget(chatInputLineEdit);
    
    sendChatButton = new QPushButton("Send", this);
    sendChatButton->setStyleSheet("padding: 8px; background-color: #2a82da; color: white; border: none;");
    sendChatButton->setEnabled(false);
    chatLayout->addWidget(sendChatButton);
    
    QLabel *responseLabel = new QLabel("Response:", this);
    chatLayout->addWidget(responseLabel);
    
    chatResponseTextEdit = new QTextEdit(this);
    chatResponseTextEdit->setReadOnly(true);
    chatResponseTextEdit->setStyleSheet("background-color: #2d2d2d;");
    chatLayout->addWidget(chatResponseTextEdit);
    
    tabWidget->addTab(chatTab, "Test Chat");
    
    mainLayout->addWidget(tabWidget);
    
    // Initialize components
    serverProcess = new QProcess(this);
    statusTimer = new QTimer(this);
    networkManager = new QNetworkAccessManager(this);
}

void MainWindow::setupTrayIcon()
{
    trayIcon = new QSystemTrayIcon(this);
    trayIcon->setToolTip("WebAI-to-API");
    
    // Create tray menu
    trayMenu = new QMenu(this);
    
    showAction = new QAction("Show Window", this);
    quitAction = new QAction("Quit", this);
    
    trayMenu->addAction(showAction);
    trayMenu->addSeparator();
    trayMenu->addAction(quitAction);
    
    trayIcon->setContextMenu(trayMenu);
    trayIcon->show();
    
    connect(trayIcon, &QSystemTrayIcon::activated, this, &MainWindow::onTrayIconActivated);
    connect(showAction, &QAction::triggered, this, &QWidget::show);
    connect(quitAction, &QAction::triggered, this, &QWidget::close);
}

void MainWindow::setupConnections()
{
    // Button connections
    connect(startStopButton, &QPushButton::clicked, this, &MainWindow::toggleServer);
    connect(testApiButton, &QPushButton::clicked, this, &MainWindow::testApi);
    connect(sendChatButton, &QPushButton::clicked, this, &MainWindow::sendChatMessage);
    connect(saveSettingsButton, &QPushButton::clicked, this, &MainWindow::onProxyChanged);
    
    // Server process connections
    connect(serverProcess, &QProcess::readyReadStandardOutput, this, &MainWindow::onServerOutput);
    connect(serverProcess, &QProcess::readyReadStandardError, this, &MainWindow::onServerOutput);
    connect(serverProcess, QOverload<int, QProcess::ExitStatus>::of(&QProcess::finished),
            this, &MainWindow::onServerFinished);
    
    // Status timer
    connect(statusTimer, &QTimer::timeout, this, &MainWindow::checkServerStatus);
    statusTimer->start(3000); // Check every 3 seconds
    
    // Enter key for chat
    connect(chatInputLineEdit, &QLineEdit::returnPressed, this, &MainWindow::sendChatMessage);
}

void MainWindow::startServer()
{
    if (m_serverRunning) return;
    
    m_serverPort = portLineEdit->text().isEmpty() ? "6969" : portLineEdit->text();
    
    log(QString("Starting server on port %1...").arg(m_serverPort));
    
    // Get the path to the Python script
    QString appPath = QCoreApplication::applicationDirPath();
    QString pythonScript = QDir::toNativeSeparators(appPath + "/../src/run.py");
    
    // For now, we'll try to run it from the project root
    pythonScript = "src/run.py";
    
    // Start the Python server process
    serverProcess->setWorkingDirectory(QCoreApplication::applicationDirPath() + "/..");
    serverProcess->start("poetry", QStringList() << "run" << "python" << pythonScript);
    
    if (!serverProcess->waitForStarted()) {
        log("ERROR: Failed to start server process");
        QMessageBox::critical(this, "Error", "Failed to start the server. Make sure Poetry is installed.");
        return;
    }
    
    log("Server process started...");
}

void MainWindow::stopServer()
{
    if (!m_serverRunning) return;
    
    log("Stopping server...");
    serverProcess->terminate();
    
    if (!serverProcess->waitForFinished(5000)) {
        log("Force killing server...");
        serverProcess->kill();
    }
    
    updateStatus("Server stopped", false);
}

void MainWindow::toggleServer()
{
    if (m_serverRunning) {
        stopServer();
    } else {
        startServer();
    }
}

void MainWindow::testApi()
{
    if (!m_serverRunning) {
        QMessageBox::warning(this, "Server Not Running", "Please start the server first.");
        return;
    }
    
    log("Testing API endpoint...");
    
    QUrl url(QString("http://localhost:%1/v1/models").arg(m_serverPort));
    QNetworkRequest request(url);
    
    QNetworkReply *reply = networkManager->get(request);
    connect(reply, &QNetworkReply::finished, [this, reply]() {
        if (reply->error() == QNetworkReply::NoError) {
            QByteArray response = reply->readAll();
            log(QString("API Test Success: %1").arg(QString(response).left(200)));
            
            // Also try chat endpoint
            testApiChat();
        } else {
            log(QString("API Test Failed: %1").arg(reply->errorString()));
        }
        reply->deleteLater();
    });
}

void MainWindow::testApiChat()
{
    QUrl url(QString("http://localhost:%1/v1/chat/completions").arg(m_serverPort));
    QNetworkRequest request(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    
    QJsonObject json;
    json["model"] = "gemini-2.5-flash";
    json["messages"] = QJsonArray{{QJsonObject{{"role", "user"}, {"content", "Hello!"}}}};
    
    QByteArray postData = QJsonDocument(json).toJson();
    
    QNetworkReply *reply = networkManager->post(request, postData);
    connect(reply, &QNetworkReply::finished, [this, reply]() {
        if (reply->error() == QNetworkReply::NoError) {
            QByteArray response = reply->readAll();
            log(QString("Chat API Success!"));
            onApiResponse(QString(response));
        } else {
            log(QString("Chat API Error: %1").arg(reply->errorString()));
        }
        reply->deleteLater();
    });
}

void MainWindow::sendChatMessage()
{
    if (!m_serverRunning) {
        QMessageBox::warning(this, "Server Not Running", "Please start the server first.");
        return;
    }
    
    QString message = chatInputLineEdit->text().trimmed();
    if (message.isEmpty()) return;
    
    log(QString("Sending: %1").arg(message));
    chatInputLineEdit->clear();
    
    QUrl url(QString("http://localhost:%1/v1/chat/completions").arg(m_serverPort));
    QNetworkRequest request(url);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    
    QString model = modelComboBox->currentText();
    
    QJsonObject json;
    json["model"] = model;
    json["messages"] = QJsonArray{{QJsonObject{{"role", "user"}, {"content", message}}}};
    
    QByteArray postData = QJsonDocument(json).toJson();
    
    QNetworkReply *reply = networkManager->post(request, postData);
    connect(reply, &QNetworkReply::finished, [this, reply]() {
        if (reply->error() == QNetworkReply::NoError) {
            QByteArray response = reply->readAll();
            onApiResponse(QString(response));
        } else {
            chatResponseTextEdit->append(QString("Error: %1").arg(reply->errorString()));
        }
        reply->deleteLater();
    });
}

void MainWindow::onApiResponse(const QString &response)
{
    QJsonDocument doc = QJsonDocument::fromJson(response.toUtf8());
    if (!doc.isObject()) {
        chatResponseTextEdit->append(response);
        return;
    }
    
    QJsonObject obj = doc.object();
    
    // Try to extract the message content
    if (obj.contains("choices")) {
        QJsonArray choices = obj["choices"].toArray();
        if (!choices.isEmpty()) {
            QJsonObject choice = choices[0].toObject();
            if (choice.contains("message")) {
                QJsonObject message = choice["message"].toObject();
                QString content = message["content"].toString();
                chatResponseTextEdit->append(QString("AI: %1").arg(content));
                log(QString("Received response: %1").arg(content.left(50)));
                return;
            }
        }
    }
    
    chatResponseTextEdit->append(response);
}

void MainWindow::clearLog()
{
    logTextEdit->clear();
}

void MainWindow::onTrayIconActivated(QSystemTrayIcon::ActivationReason reason)
{
    if (reason == QSystemTrayIcon::Trigger || reason == QSystemTrayIcon::DoubleClick) {
        show();
        raise();
        activateWindow();
    }
}

void MainWindow::onServerOutput()
{
    QByteArray output = serverProcess->readAll();
    QString text = QString::fromUtf8(output).trimmed();
    if (!text.isEmpty()) {
        log(text);
        
        // Check if server is ready
        if (text.contains("Uvicorn running on") || text.contains("Application startup complete")) {
            updateStatus("Server running", true);
        }
    }
}

void MainWindow::onServerFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    Q_UNUSED(exitCode);
    Q_UNUSED(exitStatus);
    
    log("Server process finished");
    updateStatus("Server stopped", false);
}

void MainWindow::checkServerStatus()
{
    // Check if server is responding
    if (!m_serverRunning) return;
    
    QUrl url(QString("http://localhost:%1/").arg(m_serverPort));
    QNetworkRequest request(url);
    
    QNetworkReply *reply = networkManager->get(request);
    reply->setProperty("statusCheck", true);
    
    connect(reply, &QNetworkReply::finished, [this, reply]() {
        bool isRunning = (reply->error() == QNetworkReply::NoError);
        if (isRunning != m_serverRunning) {
            updateStatus(isRunning ? "Server running" : "Server stopped", isRunning);
        }
        reply->deleteLater();
    });
}

void MainWindow::updateStatus(const QString &status, bool isRunning)
{
    m_serverRunning = isRunning;
    
    statusLabel->setText(QString("Status: %1").arg(status));
    serverStatusLabel->setText(QString("Server: %1").arg(isRunning ? "Running" : "Stopped"));
    serverStatusLabel->setStyleSheet(QString("color: %1; font-weight: bold;").arg(isRunning ? "#4CAF50" : "#ff6b6b"));
    
    startStopButton->setText(isRunning ? "Stop Server" : "Start Server");
    startStopButton->setStyleSheet(QString("padding: 10px; font-weight: bold; background-color: %1; color: white; border: none;")
                                    .arg(isRunning ? "#f44336" : "#4CAF50"));
    
    testApiButton->setEnabled(isRunning);
    chatInputLineEdit->setEnabled(isRunning);
    sendChatButton->setEnabled(isRunning);
    
    if (isRunning) {
        log("Server is now running!");
    }
}

bool MainWindow::isServerRunning() const
{
    return m_serverRunning;
}

void MainWindow::onBrowserSelected(int index)
{
    Q_UNUSED(index);
    log(QString("Browser selected: %1").arg(browserComboBox->currentText()));
}

void MainWindow::onProxyChanged()
{
    QString proxy = proxyLineEdit->text();
    log(QString("Proxy changed to: %1").arg(proxy.isEmpty() ? "(none)" : proxy));
    QMessageBox::information(this, "Settings", "Settings saved! Restart server for changes to take effect.");
}

void MainWindow::onModelSelected(int index)
{
    Q_UNUSED(index);
    log(QString("Model selected: %1").arg(modelComboBox->currentText()));
}

void MainWindow::log(const QString &message)
{
    QString timestamp = QTime::currentTime().toString("hh:mm:ss");
    logTextEdit->append(QString("[%1] %2").arg(timestamp, message));
}

void MainWindow::closeEvent(QCloseEvent *event)
{
    if (trayIcon->isVisible()) {
        hide();
        event->ignore();
    } else {
        if (m_serverRunning) {
            stopServer();
        }
        event->accept();
    }
}


#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QSystemTrayIcon>
#include <QMenu>
#include <QAction>
#include <QTimer>
#include <QProcess>
#include <QLabel>
#include <QPushButton>
#include <QTextEdit>
#include <QLineEdit>
#include <QComboBox>
#include <QGroupBox>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QTableWidget>
#include <QTabWidget>
#include <QMessageBox>
#include <QNetworkAccessManager>
#include <QNetworkRequest>
#include <QNetworkReply>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    void startServer();
    void stopServer();
    void toggleServer();
    void testApi();
    void clearLog();
    void onTrayIconActivated(QSystemTrayIcon::ActivationReason reason);
    void onServerOutput();
    void onServerFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void checkServerStatus();
    void onBrowserSelected(int index);
    void onProxyChanged();
    void onModelSelected(int index);
    void sendChatMessage();
    void onApiResponse(const QString &response);

private:
    void setupUi();
    void setupTrayIcon();
    void setupConnections();
    void log(const QString &message);
    void updateStatus(const QString &status, bool isRunning);
    bool isServerRunning() const;

    // UI Components
    QWidget *centralWidget;
    QTabWidget *tabWidget;
    
    // Status tab
    QLabel *statusLabel;
    QLabel *serverStatusLabel;
    QPushButton *startStopButton;
    QPushButton *testApiButton;
    QTextEdit *logTextEdit;
    QLabel *portLabel;
    QLineEdit *portLineEdit;
    
    // Settings tab
    QComboBox *browserComboBox;
    QLineEdit *proxyLineEdit;
    QComboBox *modelComboBox;
    QPushButton *saveSettingsButton;
    
    // Test Chat tab
    QLineEdit *chatInputLineEdit;
    QPushButton *sendChatButton;
    QTextEdit *chatResponseTextEdit;
    
    // System Tray
    QSystemTrayIcon *trayIcon;
    QMenu *trayMenu;
    QAction *showAction;
    QAction *quitAction;
    
    // Backend process
    QProcess *serverProcess;
    QTimer *statusTimer;
    QNetworkAccessManager *networkManager;
    
    bool m_serverRunning;
    QString m_serverPort;
};

#endif // MAINWINDOW_H


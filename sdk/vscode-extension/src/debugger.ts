import * as vscode from 'vscode';
import { IExtensionApi } from './types/pythonExtensionApi';

export class RemoteDebuggerManager {
    constructor(private pythonApi: IExtensionApi) {}

    /**
     * Obtains the remote debug command and launches debugpy server either in a terminal
     * or by starting an interactive VS Code attach debug session.
     */
    public async launchRemoteDebugger(
        targetScript?: string,
        customHost?: string,
        customPort?: number,
        waitForClient: boolean = true
    ): Promise<void> {
        const config = vscode.workspace.getConfiguration('sr.python');
        const host = customHost || config.get<string>('remoteDebugHost', 'localhost');
        const port = customPort || config.get<number>('remoteDebugPort', 5678);

        vscode.window.showInformationMessage(
            `🚀 S&R CoreSync: جاري تحضير أمر تشغيل debugpy عن بُعد على ${host}:${port}...`
        );

        try {
            // 1. استخراج أمر تشغيل debugpy من إضافة بايثون الرسمية
            const launcherCommandParts = await this.pythonApi.debug.getRemoteLauncherCommand(
                host,
                port,
                waitForClient
            );

            const debuggerPath = await this.pythonApi.debug.getDebuggerPackagePath();

            // 2. تجميع الأمر البرمجي الكامل مع السكربت الهدف إن وُجد
            const fullCommandArray = [...launcherCommandParts];
            if (targetScript) {
                fullCommandArray.push(targetScript);
            }

            const commandString = fullCommandArray.map((arg) => (arg.includes(' ') ? `"${arg}"` : arg)).join(' ');

            // 3. فتح طرفية طرفية (Terminal) لتشغيل خادم المصحح
            const terminal = vscode.window.createTerminal({
                name: `S&R debugpy Server (${host}:${port})`
            });
            terminal.show();
            terminal.sendText(commandString);

            vscode.window.showInformationMessage(
                `✅ تم تشغيل خادم debugpy على ${host}:${port}. مسار الحزمة: ${debuggerPath || 'مدمج'}`
            );

            // 4. خيار إرفاق مصحح VS Code تلقائياً بعد تشغيل الخادم
            const attachChoice = await vscode.window.showQuickPick(['نعم، اربط مصحح VS Code الآن', 'لا، سأربطه يدوياً'], {
                placeHolder: 'هل ترغب في بدء جلسة التصحيح ومراقبة المتغيرات فوراً؟'
            });

            if (attachChoice === 'نعم، اربط مصحح VS Code الآن') {
                await this.attachToRemoteDebugger(host, port);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`❌ فشل تشغيل مصحح debugpy عن بُعد: ${error}`);
        }
    }

    /**
     * Start a VS Code debugging session attaching to the remote debugpy server.
     */
    public async attachToRemoteDebugger(host: string, port: number): Promise<void> {
        const debugConfiguration: vscode.DebugConfiguration = {
            name: `S&R Python: Attach to Remote (${host}:${port})`,
            type: 'python',
            request: 'attach',
            connect: {
                host,
                port
            },
            pathMappings: [
                {
                    localRoot: '${workspaceFolder}',
                    remoteRoot: '.'
                }
            ],
            justMyCode: false
        };

        const started = await vscode.debug.startDebugging(undefined, debugConfiguration);
        if (started) {
            vscode.window.showInformationMessage(`🔗 تم ربط مصحح VS Code بنجاح مع ${host}:${port}`);
        } else {
            vscode.window.showWarningMessage(`⚠️ تعذر ربط مصحح VS Code بالجلسة البعيدة على ${host}:${port}`);
        }
    }
}

import * as vscode from 'vscode';
import { IExtensionApi } from './types/pythonExtensionApi';

export class PythonEnvironmentExecutor {
    constructor(private pythonApi: IExtensionApi) {}

    /**
     * Resolves the exact python command array for a given resource or workspace.
     */
    public getPythonCommand(resource?: vscode.Uri): string[] | undefined {
        const details = this.pythonApi.settings.getExecutionDetails(resource);
        return details.execCommand;
    }

    /**
     * Executes a Python script in an integrated terminal using the active environment.
     */
    public executeScriptInTerminal(scriptPath: string, args: string[] = [], resource?: vscode.Uri): void {
        const command = this.getPythonCommand(resource);

        if (!command || command.length === 0) {
            vscode.window.showErrorMessage(
                '⚠️ لم يتم العثور على مفسر بايثون صالح! يرجى اختيار بيئة العمل (Python Interpreter) في أسفل المحرر أولاً.'
            );
            return;
        }

        const fullCommand = [...command, `"${scriptPath}"`, ...args].join(' ');

        const terminal = vscode.window.createTerminal({
            name: 'S&R CoreSync Python Runner'
        });
        terminal.show();
        terminal.sendText(fullCommand);

        vscode.window.showInformationMessage(
            `🚀 جاري تشغيل السكربت عبر البيئة: ${command.join(' ')}`
        );
    }
}

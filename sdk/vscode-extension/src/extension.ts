import * as vscode from 'vscode';
import { IExtensionApi } from './types/pythonExtensionApi';
import { CoreSyncDataViewerProvider } from './dataProvider';
import { RemoteDebuggerManager } from './debugger';
import { PythonEnvironmentExecutor } from './executor';

let statusBarItem: vscode.StatusBarItem;

export async function activate(context: vscode.ExtensionContext) {
    console.log('🌟 [S&R CoreSync] تفعيل إضافة Python & Data Science Toolkit...');

    // 1. الوصول إلى إضافة بايثون الرسمية
    const pythonExtension = vscode.extensions.getExtension<IExtensionApi>('ms-python.python');
    if (!pythonExtension) {
        vscode.window.showErrorMessage(
            '❌ إضافة بايثون الرسمية (ms-python.python) غير مثبتة! يرجى تثبيتها من سوق إضافات VS Code.'
        );
        return;
    }

    if (!pythonExtension.isActive) {
        await pythonExtension.activate();
    }

    const pythonApi = pythonExtension.exports;

    // 2. انتظار اكتمال تهيئة إضافة بايثون (ready promise)
    await pythonApi.ready;

    // 3. تهيئة المديرين المتخصصين (Option 1, 2, 3)
    const executor = new PythonEnvironmentExecutor(pythonApi);
    const debuggerManager = new RemoteDebuggerManager(pythonApi);

    // 4. إعداد عنصر شريط الحالة (Status Bar Item)
    statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
    statusBarItem.command = 'sr.openDataViewer';
    context.subscriptions.push(statusBarItem);
    updateStatusBar(pythonApi);

    // 5. الاستماع التلقائي لتغييرات المفسر والبيئة
    context.subscriptions.push(
        pythonApi.settings.onDidChangeExecutionDetails((uri) => {
            updateStatusBar(pythonApi, uri);
            const cmd = pythonApi.settings.getExecutionDetails(uri).execCommand;
            vscode.window.showInformationMessage(
                `🔄 تم تحديث بيئة بايثون تلقائياً: ${cmd ? cmd.join(' ') : 'غير محدد'}`
            );
        })
    );

    // ─── الأمر الأول: تشغيل السكربت بالبيئة المعتمدة ───
    const runScriptCmd = vscode.commands.registerCommand('sr.runPythonScript', () => {
        const activeEditor = vscode.window.activeTextEditor;
        if (!activeEditor || activeEditor.document.languageId !== 'python') {
            vscode.window.showWarningMessage('يرجى فتح ملف بايثون (.py) لتشغيله.');
            return;
        }

        const filePath = activeEditor.document.uri.fsPath;
        executor.executeScriptInTerminal(filePath, [], activeEditor.document.uri);
    });

    // ─── الأمر الثاني: فتح عارض البيانات التفاعلي (Data Viewer) ───
    const openDataViewerCmd = vscode.commands.registerCommand('sr.openDataViewer', async () => {
        vscode.window.showInformationMessage('📊 جاري تجهيز عارض البيانات التفاعلي (Data Viewer)...');

        // نموذج بيانات افتراضي تجريبي
        const sampleRecords: Record<string, unknown>[] = [
            { id: 1, service: 'Sovereign AI Engine', latencyMs: 32, status: 'Active', tier: 'Enterprise' },
            { id: 2, service: 'FinTech Escrow Core', latencyMs: 45, status: 'Active', tier: 'FinTech' },
            { id: 3, service: 'Satellite QKD Link', latencyMs: 12, status: 'Active', tier: 'Sovereign' },
            { id: 4, service: 'High-Speed CDN Edge', latencyMs: 8, status: 'Optimal', tier: 'Global' },
            { id: 5, service: 'Zero-Knowledge Proof Enclave', latencyMs: 64, status: 'Active', tier: 'Security' }
        ];

        const provider = new CoreSyncDataViewerProvider(sampleRecords);

        try {
            await pythonApi.datascience.showDataViewer(
                provider,
                'S&R CoreSync • مصفوفة تحليلات الأنظمة الذكية'
            );
            vscode.window.showInformationMessage('✅ تم فتح عارض البيانات التفاعلي بنجاح!');
        } catch (err) {
            vscode.window.showErrorMessage(`❌ تعذر فتح عارض البيانات: ${err}`);
        }
    });

    // ─── الأمر الثالث: تشغيل مصحح الأخطاء عن بُعد (debugpy) ───
    const startDebuggerCmd = vscode.commands.registerCommand('sr.startRemoteDebugger', async () => {
        const activeEditor = vscode.window.activeTextEditor;
        const targetPath = activeEditor?.document.languageId === 'python' ? activeEditor.document.uri.fsPath : undefined;

        await debuggerManager.launchRemoteDebugger(targetPath);
    });

    context.subscriptions.push(runScriptCmd, openDataViewerCmd, startDebuggerCmd);
    vscode.window.showInformationMessage('🚀 [S&R CoreSync] الإضافة جاهزة بكامل مزايا بايثون والتصحيح وعارض البيانات!');
}

function updateStatusBar(api: IExtensionApi, uri?: vscode.Uri) {
    const details = api.settings.getExecutionDetails(uri);
    if (details.execCommand && details.execCommand.length > 0) {
        const name = details.execCommand[0].split(/[\\/]/).pop() || 'python';
        statusBarItem.text = `$(symbol-event) S&R: ${name}`;
        statusBarItem.tooltip = `أمر التنفيذ: ${details.execCommand.join(' ')}\nانقر لفتح عارض البيانات`;
        statusBarItem.show();
    } else {
        statusBarItem.text = '$(alert) S&R: اختر مفسر بايثون';
        statusBarItem.tooltip = 'لم يتم تحديد مفسر بايثون لهذا المشروع';
        statusBarItem.show();
    }
}

export function deactivate() {
    if (statusBarItem) {
        statusBarItem.dispose();
    }
}

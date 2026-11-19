import { Event, Uri } from 'vscode';

export type Resource = Uri | undefined;

export interface IRange {
    startRow: number;
    startColumn: number;
    endRow: number;
    endColumn: number;
}

export interface IDataViewerRows {
    data: Record<string, unknown>[];
    rowCount: number;
    columnNames: string[];
    columns: { key: string; name: string; type: string }[];
}

export interface IDataViewerDataProvider {
    /**
     * Get the total row count of the dataset.
     */
    getRowCount(): Promise<number>;

    /**
     * Fetch a slice/window of rows.
     */
    getRows(start: number, end: number): Promise<Record<string, unknown>[]>;

    /**
     * Fetch column metadata for the dataset.
     */
    getColumns(): Promise<{ key: string; name: string; type: string }[]>;

    /**
     * Dispose resources when viewer closes.
     */
    dispose(): void;
}

export interface IExtensionApi {
    /**
     * Promise indicating whether all parts of the extension have completed loading or not.
     */
    ready: Promise<void>;
    debug: {
        /**
         * Generate an array of strings for commands to pass to the Python executable to launch the debugger for remote debugging.
         */
        getRemoteLauncherCommand(host: string, port: number, waitUntilDebuggerAttaches?: boolean): Promise<string[]>;

        /**
         * Gets the path to the debugger package used by the extension.
         */
        getDebuggerPackagePath(): Promise<string | undefined>;
    };
    /**
     * Return internal settings within the extension which are stored in VSCode storage.
     */
    settings: {
        /**
         * An event that is emitted when execution details change.
         */
        readonly onDidChangeExecutionDetails: Event<Uri | undefined>;

        /**
         * Returns all details needed to execute code within the selected environment.
         */
        getExecutionDetails(resource?: Resource): {
            execCommand: string[] | undefined;
        };
    };
    datascience: {
        /**
         * Launches Data Viewer component.
         */
        showDataViewer(dataProvider: IDataViewerDataProvider, title: string): Promise<void>;
    };
}

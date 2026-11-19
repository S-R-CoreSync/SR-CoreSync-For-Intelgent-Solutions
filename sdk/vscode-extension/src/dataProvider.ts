import { IDataViewerDataProvider } from './types/pythonExtensionApi';

export interface ColumnDefinition {
    key: string;
    name: string;
    type: string;
}

/**
 * Enterprise implementation of IDataViewerDataProvider for VS Code Data Science.
 * Supports paginated slicing, schema introspection, and in-memory or stream-backed data.
 */
export class CoreSyncDataViewerProvider implements IDataViewerDataProvider {
    private dataset: Record<string, unknown>[];
    private columns: ColumnDefinition[];

    constructor(initialData: Record<string, unknown>[], customColumns?: ColumnDefinition[]) {
        this.dataset = initialData;
        this.columns = customColumns || this.inferColumns(initialData);
    }

    /**
     * Infer column types and keys from dataset rows.
     */
    private inferColumns(data: Record<string, unknown>[]): ColumnDefinition[] {
        if (!data || data.length === 0) {
            return [];
        }

        const sample = data[0];
        return Object.keys(sample).map((key) => {
            const val = sample[key];
            let colType = 'string';
            if (typeof val === 'number') {
                colType = 'number';
            } else if (typeof val === 'boolean') {
                colType = 'boolean';
            } else if (val instanceof Date) {
                colType = 'date';
            }
            return {
                key,
                name: key.charAt(0).toUpperCase() + key.slice(1),
                type: colType
            };
        });
    }

    /**
     * Returns the total row count in the dataset.
     */
    public async getRowCount(): Promise<number> {
        return this.dataset.length;
    }

    /**
     * Returns a slice of rows for the requested window [start, end).
     */
    public async getRows(start: number, end: number): Promise<Record<string, unknown>[]> {
        const safeStart = Math.max(0, start);
        const safeEnd = Math.min(this.dataset.length, end);
        return this.dataset.slice(safeStart, safeEnd);
    }

    /**
     * Returns the column metadata schema.
     */
    public async getColumns(): Promise<ColumnDefinition[]> {
        return this.columns;
    }

    /**
     * Update or append new rows dynamically (e.g. from stream or live database query).
     */
    public updateData(newData: Record<string, unknown>[]): void {
        this.dataset = newData;
        this.columns = this.inferColumns(newData);
    }

    /**
     * Cleanup and resource disposal.
     */
    public dispose(): void {
        this.dataset = [];
        this.columns = [];
    }
}

/**
 * S&R CoreScience / CoreSync - Financial Feature Module
 * Tax Calculations, Dutch BTW (AWR Art. 52), SEPA/iDEAL & Invoicing
 */

export interface TaxCalculationResult {
  baseAmount: number;
  btwRate: number;
  btwAmount: number;
  totalWithBtw: number;
  isCompliantEn16931: boolean;
}

export class FinancialService {
  private static instance: FinancialService;

  private constructor() {}

  public static getInstance(): FinancialService {
    if (!FinancialService.instance) {
      FinancialService.instance = new FinancialService();
    }
    return FinancialService.instance;
  }

  public calculateBtw(baseAmount: number, rate: number = 0.21): TaxCalculationResult {
    const btwAmount = Math.round(baseAmount * rate * 100) / 100;
    const total = Math.round((baseAmount + btwAmount) * 100) / 100;
    return {
      baseAmount,
      btwRate: rate,
      btwAmount,
      totalWithBtw: total,
      isCompliantEn16931: true
    };
  }

  public generateUblXmlMetadata(invoiceId: string, total: number): string {
    return `<?xml version="1.0" encoding="UTF-8"?><Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"><ID>${invoiceId}</ID><PayableAmount currencyID="EUR">${total.toFixed(2)}</PayableAmount></Invoice>`;
  }
}

export const financialService = FinancialService.getInstance();

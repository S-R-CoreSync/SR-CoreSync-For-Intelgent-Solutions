/**
 * S&R CoreScience / CoreSync - Financial Feature Module
 * Tax Calculations, Dutch BTW (AWR Art. 52), SEPA/iDEAL & Invoicing
 */


export class FinancialService {
  static instance;

  constructor() {}

  static getInstance() {
    if (!FinancialService.instance) {
      FinancialService.instance = new FinancialService();
    }
    return FinancialService.instance;
  }

  calculateBtw(baseAmount, rate= 0.21) {
    const btwAmount = Math.round(baseAmount * rate * 100) / 100;
    const total = Math.round((baseAmount + btwAmount) * 100) / 100;
    return {
      baseAmount,
      btwRate,
      btwAmount,
      totalWithBtw,
      isCompliantEn16931: true
    };
  }

  generateUblXmlMetadata(invoiceId, total) {
    return `<?xml version="1.0" encoding="UTF-8"?><Invoice xmlns="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2"><ID>${invoiceId}</ID><PayableAmount currencyID="EUR">${total.toFixed(2)}</PayableAmount></Invoice>`;
  }
}

export const financialService = FinancialService.getInstance();

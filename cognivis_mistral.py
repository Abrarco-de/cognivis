def titanium_cleaner(df):
    # --- 1. Standardize headers ---
    df.columns = [c.lower().replace(' ', '_').strip() for c in df.columns]

    # --- 2. Alias Mapping ---
    mapping = {
        'total': 'amount_sar', 'price': 'amount_sar', 'grand_total': 'amount_sar', 'amount': 'amount_sar',
        'vat_id': 'customer_vat_id', 'tax_id': 'customer_vat_id', 'vat_number': 'customer_vat_id',
        'item': 'category', 'product_category': 'category', 'dept': 'category', 'type': 'category',
        'inv_id': 'invoice_id', 'bill_no': 'invoice_id', 'invoice_no': 'invoice_id'
    }

    df = df.rename(columns=mapping)

    # --- 3. Ensure Required Columns Exist ---
    required_cols = ['invoice_id', 'amount_sar', 'customer_vat_id', 'category']

    for col in required_cols:
        if col not in df.columns:
            if col == 'invoice_id':
                df[col] = [f"INV-{i+1}" for i in range(len(df))]
            elif col == 'amount_sar':
                df[col] = 0.0
            elif col == 'customer_vat_id':
                df[col] = ""
            elif col == 'category':
                df[col] = "Uncategorized"

    # --- 4. Clean Amount (Robust) ---
    df['amount_sar'] = (
        df['amount_sar']
        .astype(str)
        .str.replace(r'[^\d.]', '', regex=True)
        .replace('', '0')
    )
    df['amount_sar'] = pd.to_numeric(df['amount_sar'], errors='coerce').fillna(0)

    # --- 5. Clean VAT ID (FIXED HERE) ---
    df['customer_vat_id'] = (
        df['customer_vat_id']
        .fillna('')
        .astype(str)
        .str.strip()
    )

    # --- 6. Clean Category ---
    df['category'] = df['category'].fillna("Uncategorized").astype(str).str.strip()

    # --- 7. Remove Completely Empty Rows ---
    df = df.dropna(how='all')

    return df

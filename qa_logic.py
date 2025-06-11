def score_lead(company):
    """
    Apply Caprae's acquisition criteria to a company record.
    Returns (score, justification) where score is 'Green', 'Yellow', or 'Red'.
    """
    try:
        emp_count = company.get('Employee Count')
        revenue = company.get('Revenue')
        location = company.get('HQ State', '')
        # Clean up values
        if emp_count in [None, '', 'None', '000', 0]:
            return 'Yellow', 'Missing employee count.'
        if revenue in [None, '', 'None', '000', 0]:
            return 'Yellow', 'Missing revenue.'
        try:
            emp_count = int(str(emp_count).replace(',', '').strip())
        except Exception:
            return 'Yellow', 'Unparseable employee count.'
        try:
            revenue = int(str(revenue).replace(',', '').replace('$', '').strip())
        except Exception:
            return 'Yellow', 'Unparseable revenue.'
        if emp_count < 50 or emp_count > 5000:
            return 'Red', 'Employee count out of range.'
        if revenue < 5000000 or revenue > 500000000:
            return 'Red', 'Revenue out of range.'
        if not location or location in ['None', '', None]:
            return 'Yellow', 'Missing location.'
        if location not in ['CA', 'NY', 'TX', 'IL', 'FL', 'MA', 'WA', 'GA', 'PA', 'OH', 'MI']:
            return 'Yellow', 'Location not in top target states.'
        return 'Green', 'Strong fit based on all criteria.'
    except Exception as e:
        return 'Yellow', f'Partial fit or missing data: {e}' 
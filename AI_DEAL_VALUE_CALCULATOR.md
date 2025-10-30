# AI-Powered Deal Value Calculator
**Intelligent Quote Revision Detection & Automatic Deal Value Calculation**

---

## 🎯 Overview

The AI-Powered Deal Value Calculator is a sophisticated feature that automatically calculates and updates deal values for projects in your pipeline by intelligently analyzing quotation data and handling quote revisions.

### The Problem It Solves

Previously, when projects had multiple quote revisions (e.g., R01, R02, R03), there was a risk of:
- **Double-counting** quotation values from different revisions
- **Manual errors** when calculating total deal values
- **Outdated values** when quotes were revised
- **System duplicates** when multiple quotes existed for the same system

### The AI Solution

The calculator uses **intelligent pattern recognition** to:
1. **Detect quote revisions** automatically (QT-ACS-Sup-BEDROCK-18425-R**02**)
2. **Select only the latest revision** of each quote
3. **Avoid system duplicates** (won't count two quotes for the same system)
4. **Automatically sum** quotation selling prices to calculate deal value

---

## 🤖 AI Methodology

### 1. Quote Reference Parsing

The system uses regex pattern matching to extract:
- **Base quote reference**: `QT-ACS-Sup-BEDROCK-18425`
- **Revision number**: `R02` = Revision 2

**Supported Formats:**
```
QT-ACS-Sup-BEDROCK-18425-R02  → Base: QT-ACS-Sup-BEDROCK-18425, Rev: 2
CS-EJT-LC-AHHOBP-13725-R07     → Base: CS-EJT-LC-AHHOBP-13725, Rev: 7
QT-EJT-BEC-DFOPK-R01           → Base: QT-EJT-BEC-DFOPK, Rev: 1
```

### 2. Revision Grouping

Quotes are grouped by their base reference:
```
Group: QT-ACS-Sup-BEDROCK-18425
├─ R01: $90,000  (Older)
└─ R02: $100,000 (Latest) ✓ SELECTED
```

### 3. Latest Revision Selection

For each group, the system selects the quote with:
1. **Highest revision number** (R07 > R05 > R01)
2. **Most recent date** (if revision numbers are equal)

### 4. System Deduplication

If multiple quotes exist for the same system (e.g., "ACS"), only the latest one is included:
```
System: ACS
├─ QT-ACS-Sup-BEDROCK-18425-R01 ($90K, Rev 1)  → Excluded
└─ QT-ACS-Sup-BEDROCK-18425-R02 ($100K, Rev 2) → Included ✓
```

---

## 📊 Real-World Example

### Scenario: Office Design Project

**Quotations in System:**
| Quote Reference | System | Price | Revision | Status |
|----------------|--------|--------|----------|---------|
| QT-ACS-Sup-BEDROCK-18425-R01 | ACS | $90,000 | 1 | ❌ Excluded (older) |
| **QT-ACS-Sup-BEDROCK-18425-R02** | **ACS** | **$100,000** | **2** | **✓ Included** |
| QT-EJT-ACS-HIK-BEDROCK-14425-R01 | ACS | $50,000 | 1 | ❌ Excluded (duplicate system) |
| CS-EJT-LC-AHHOBP-13725-R05 | IP-CCTV | $140,000 | 5 | ❌ Excluded (older) |
| **CS-EJT-LC-AHHOBP-13725-R07** | **IP-CCTV** | **$150,000** | **7** | **✓ Included** |

**AI Calculation:**
```
Deal Value = $100,000 (ACS, latest) + $150,000 (IP-CCTV, latest)
           = $250,000
```

**Without AI (Manual Calculation Risk):**
```
Could mistakenly sum all quotes:
$90K + $100K + $50K + $140K + $150K = $530,000 ❌ WRONG!
(More than double the actual value)
```

---

## 🚀 How to Use

### Method 1: Admin Interface (Bulk Update)

1. **Login** as General Manager or Technical Team Leader
2. **Navigate** to: `/admin/update_deal_values`
3. **Review** the information page showing:
   - Total projects to be processed
   - How the AI logic works
   - Example calculations
4. **Click** "Calculate & Update Deal Values"
5. **Review Results** showing:
   - Projects updated
   - Old vs New values
   - Quotations included for each project

### Method 2: API Endpoint (Individual Project)

For programmatic access or custom integrations:

```javascript
// Calculate deal value for a specific project
fetch('/api/calculate_deal_value/Office design fit-out project')
  .then(response => response.json())
  .then(data => {
    console.log('Deal Value:', data.deal_value);
    console.log('Included Quotes:', data.quotes);
  });
```

**Response Format:**
```json
{
  "success": true,
  "deal_value": 250000.00,
  "quotes": [
    {
      "quote_ref": "QT-ACS-Sup-BEDROCK-18425-R02",
      "price": 100000.00,
      "system": "ACS",
      "revision": 2
    },
    {
      "quote_ref": "CS-EJT-LC-AHHOBP-13725-R07",
      "price": 150000.00,
      "system": "IP-CCTV",
      "revision": 7
    }
  ]
}
```

---

## 🔧 Technical Implementation

### Core Functions

#### 1. `parse_quote_reference(quote_ref)`
Extracts base reference and revision number from quote string.

```python
parse_quote_reference("QT-ACS-Sup-BEDROCK-18425-R02")
# Returns: ("QT-ACS-Sup-BEDROCK-18425", 2)
```

#### 2. `get_latest_quote_revisions(quotes)`
Groups quotes by base reference and selects latest revision.

```python
quotes = [
    ("QT-ACS-R01", 90000, "2025-01-01", "ACS"),
    ("QT-ACS-R02", 100000, "2025-02-01", "ACS")
]
latest = get_latest_quote_revisions(quotes)
# Returns: [{"quote_ref": "QT-ACS-R02", "price": 100000, ...}]
```

#### 3. `filter_duplicates_by_system(quotes)`
Removes duplicate quotes for the same system.

```python
quotes = [
    {"quote_ref": "QT-ACS-A-R02", "system": "ACS", "revision": 2},
    {"quote_ref": "QT-ACS-B-R01", "system": "ACS", "revision": 1}
]
filtered = filter_duplicates_by_system(quotes)
# Returns: [{"quote_ref": "QT-ACS-A-R02", ...}] (highest revision)
```

#### 4. `calculate_deal_value_for_project(project_name)`
Main function that orchestrates the entire calculation.

```python
deal_value, quotes = calculate_deal_value_for_project("Office Project")
# Returns: (250000.00, [list of included quotes])
```

---

## 📋 Database Integration

### Tables Involved

**Source:** `projects` table
- `quote_ref` - Quote reference with revision number
- `quotation_selling_price` - Price to sum
- `system` - System type (for deduplication)
- `registered_date` - For sorting when revisions match

**Target:** `register_project` table
- `deal_value` - Automatically calculated field

### SQL Logic

```sql
-- Fetch all quotations for a project
SELECT quote_ref, quotation_selling_price, registered_date, system
FROM projects
WHERE project_name = ?
AND quotation_selling_price IS NOT NULL
AND quotation_selling_price > 0

-- Update deal value
UPDATE register_project
SET deal_value = ?
WHERE project_name = ?
```

---

## ✅ Benefits

### For Sales Teams
- ✅ **Accurate deal values** automatically calculated
- ✅ **No manual errors** from double-counting revisions
- ✅ **Always up-to-date** values in pipeline
- ✅ **Clear visibility** of which quotes are included

### For Management
- ✅ **Reliable pipeline forecasting**
- ✅ **Accurate revenue projections**
- ✅ **Audit trail** of calculations
- ✅ **Confidence in reported values**

### For System
- ✅ **Intelligent automation** reduces manual work
- ✅ **Consistent logic** applied across all projects
- ✅ **Scalable solution** works for any number of projects
- ✅ **Future-proof** handles new revision formats

---

## 🛡️ Safety Features

### Data Protection
- **Backup recommended** before bulk updates
- **Preview before commit** - review changes first
- **Transaction-based** - all or nothing updates
- **Rollback capable** - can restore from backups

### Validation
- **Null handling** - safely handles missing data
- **Float precision** - accurate to 2 decimal places
- **Error handling** - graceful failures with logging
- **Permission-based** - only admins can trigger updates

---

## 🎓 Understanding the Results

### Results Page Shows:

1. **Statistics Summary**
   - Total projects processed
   - Projects updated
   - Total value changed

2. **Detailed Changes**
   For each updated project:
   - Previous deal value
   - New calculated value
   - Change amount (+/-)
   - List of included quotations with:
     * Quote reference
     * System type
     * Price
     * Revision number

3. **Action Buttons**
   - View Pipeline (see updated values)
   - Back to Dashboard

---

## 📈 Use Cases

### 1. Initial Setup
**Situation:** Importing historical data with existing quotes  
**Solution:** Run bulk update to calculate all deal values at once

### 2. Regular Maintenance
**Situation:** Quotes are revised weekly  
**Solution:** Run monthly update to keep deal values current

### 3. Audit & Verification
**Situation:** Need to verify pipeline accuracy  
**Solution:** Run update and review which quotes contribute to each deal

### 4. Custom Integrations
**Situation:** External reporting tools need deal values  
**Solution:** Use API endpoint to fetch calculated values programmatically

---

## 🔮 Future Enhancements

Possible improvements for future versions:
- **Automatic triggers** when quotes are added/updated
- **Notification system** when deal values change significantly
- **Historical tracking** of deal value changes over time
- **Custom rules** for specific quote patterns
- **Multi-currency support** with exchange rates
- **Confidence scoring** based on quote age/status

---

## 📞 Support

### Common Questions

**Q: Will this overwrite my manual deal values?**  
A: Yes, when you run the update. Review the preview first to see what will change.

**Q: What if I have quotes without revision numbers?**  
A: They're treated as revision 0 (original) and included in calculations.

**Q: Can I exclude certain quotes?**  
A: Currently no, but you can set the price to 0 or delete the quote record.

**Q: How often should I run this?**  
A: Whenever quotes are revised or new ones are added. Monthly is recommended.

---

## ✨ Conclusion

The AI-Powered Deal Value Calculator brings **intelligence and automation** to your CRM, ensuring accurate deal values while eliminating the risk of double-counting quote revisions. It's a prime example of how AI can solve real business problems with smart pattern recognition and logical processing.

**Result:** Confident, accurate deal values that reflect the true potential value of your pipeline! 🎯

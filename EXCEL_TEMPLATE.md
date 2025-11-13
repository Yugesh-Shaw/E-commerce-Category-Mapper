# Excel Template Structure

This document describes the required Excel file format for the Category Mapper.

## File Structure

Your Excel workbook should contain **two sheets**:

### Sheet 1: "Categories"

This sheet contains your allowed marketplace categories in a hierarchical format.

**Format**: Each column represents a level in the category hierarchy.

**Example**:

| Level 1 | Level 2 | Level 3 | Level 4 |
|---------|---------|---------|---------|
| Food & Drink | Dairy | Milk | Whole Milk |
| Food & Drink | Dairy | Milk | Skimmed Milk |
| Food & Drink | Dairy | Cheese | Cheddar |
| Food & Drink | Beverages | Soft Drinks | Cola |
| Home & Garden | Furniture | Living Room | Sofas |

**Notes**:
- Categories are read left-to-right across columns
- Empty cells at the end of a row are ignored
- The script will join columns with " > " separator
- Result: "Food & Drink > Dairy > Milk > Whole Milk"

### Sheet 2: "Check"

This sheet contains your internal categories that need to be mapped.

**Format**: Single column with internal category names.

**Example**:

| Internal Category |
|-------------------|
| Organic Whole Milk 1L |
| Fresh Cheddar Cheese Block |
| Cola Soft Drink 500ml |
| Living Room Sofa Set |

**Notes**:
- Only the first column is read
- One category per row
- Can include product titles, SKU descriptions, or category names

## Output Format

After processing, the "Check" sheet will have two additional columns:

| Internal Category | Mapped Category | Check |
|-------------------|-----------------|-------|
| Organic Whole Milk 1L | Food & Drink > Dairy > Milk > Whole Milk | |
| Fresh Cheddar Cheese Block | Food & Drink > Dairy > Cheese > Cheddar | |
| Cola Soft Drink 500ml | Food & Drink > Beverages > Soft Drinks > Cola | Check |

**Column Descriptions**:
- **Internal Category**: Your original input (unchanged)
- **Mapped Category**: The selected marketplace category
- **Check**: Flag indicating manual review needed (appears when confidence is low)

## Tips for Best Results

### For "Categories" Sheet:
1. **Be Comprehensive**: Include all possible target categories
2. **Be Consistent**: Use consistent separators and naming
3. **Be Hierarchical**: Organize from broad to specific (left to right)
4. **Avoid Duplicates**: Each complete path should be unique

### For "Check" Sheet:
1. **Be Specific**: More detailed descriptions lead to better matches
2. **Be Consistent**: Similar products should use similar naming
3. **Include Keywords**: Include brand, type, size if relevant
4. **Clean Data**: Remove special characters that might confuse matching

## Example Template

You can create a template file with this structure:

```
Sheet "Categories":
Level 1              Level 2         Level 3          Level 4
Electronics          Computers       Laptops          Business Laptops
Electronics          Computers       Laptops          Gaming Laptops
Electronics          Computers       Desktops         All-in-One PCs
Electronics          Audio           Headphones       Wireless Headphones
Clothing             Men's Wear      Shirts           Casual Shirts
Clothing             Men's Wear      Shirts           Formal Shirts
Clothing             Women's Wear    Dresses          Evening Dresses

Sheet "Check":
Internal Category:
Home & Garden/Home & Kitchen/Categories/Bedding & Linens/Children's Bedding/Bedding Collections
Home & Garden/Home & Kitchen/Categories/Bedding & Linens/Bedding/Duvets & Duvet Covers/Duvets
Toys & Games/Toy Types/Pretend Play/Household Toys
Baby Products/Health & Baby Care/Bathing/Bath & Hooded Towels
Home & Garden/Home & Kitchen/Categories/Home Accessories/Seasonal Décor/Christmas/Novelty Decorations
Toys & Games/Toy Types/Kids' Furniture, Décor & Storage/Backpacks & Lunch Boxes/Backpacks
```

## File Naming

- Save your template as: `Category_mapping_template.xlsx`
- Output will be: `Category_mapping_template_Tesco.xlsx`
- Autosave will be: `Category_mapping_template_Tesco_Mapped_autosave.xlsx`
- Logs will be: `category_mapping_logs.txt` (same directory)

## Common Issues

### Issue: Categories not matching
**Solution**: Check that hierarchy levels are in correct columns and formatting is consistent

### Issue: Too many "Check" flags
**Solution**: 
- Increase similarity threshold in config
- Add more specific categories to "Categories" sheet
- Improve internal category descriptions in "Check" sheet

### Issue: Wrong mappings
**Solution**:
- Review prompt engineering in the code
- Ensure categories are properly hierarchical
- Check that most specific categories are used

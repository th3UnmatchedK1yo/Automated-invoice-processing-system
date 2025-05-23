
import json
import re

# === CONFIG ===
input_path = "data/invoices.jsonl"       # <-- Change to your input file
output_path = "data"

# Regex patterns to find fields
label_patterns = [
    (r"Đơn vị bán hàng: ([^\n]+)", "COMPANY_NAME"),
    (r"CÔNG TY [^\n]+", "COMPANY_NAME"),
    (r"Mã số thuế.*?:\s*(\d+)", "TAX_CODE"),
    (r"Ký hiệu.*?:\s*([A-Z0-9]+)", "SERIAL"),
    (r"Số.*?:\s*(\d+)", "INVOICE_NO"),
    (r"Tên đơn vị.*?:\s*([^\n]+)", "BUYER_NAME"),
    (r"Hình thức thanh toán.*?:\s*(TM/CK|Tiền mặt|Chuyển khoản)", "PAYMENT_METHOD"),
    (r"Cộng tiền hàng.*?:\s*([\d\.]+)", "TOTAL_AMOUNT"),
    (r"Tiền thuế GTGT.*?:\s*([\d\.]+)", "VAT_AMOUNT"),
    (r"Tổng tiền thanh toán.*?:\s*([\d\.]+)", "TOTAL_PAYMENT"),
]

# Read and process the input file
output_data = []

with open(input_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        text = data["text"]
        labels = []

        matched_tax_codes = []
        for pattern, label in label_patterns:
            for match in re.finditer(pattern, text):
                if match.groups():
                    span_text = match.group(1)
                    start = match.start(1)
                    end = match.end(1)
                    if label == "TAX_CODE":
                        matched_tax_codes.append((start, end))
                    else:
                        labels.append([start, end, label])

        # Assign tax codes: first as SELLER, second as BUYER if both exist
        if len(matched_tax_codes) > 0:
            labels.append([matched_tax_codes[0][0], matched_tax_codes[0][1], "SELLER_TAX_CODE"])
        if len(matched_tax_codes) > 1:
            labels.append([matched_tax_codes[1][0], matched_tax_codes[1][1], "BUYER_TAX_CODE"])

        data["label"] = labels
        output_data.append(data)

# Save to output
with open(output_path, "w", encoding="utf-8") as fout:
    for item in output_data:
        fout.write(json.dumps(item, ensure_ascii=False) + "\n")
print(f"Labeled output saved to: {output_path}")

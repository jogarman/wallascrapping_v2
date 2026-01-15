
#product_files = ['20250224_0_gopro 10_as_good_as_new.csv', '20250224_0_gopro 10_new.csv', '20250224_1_gopro 10_as_good_as_new.csv', '20250224_1_gopro 10_new.csv']

def get_scan_number(product_files):
    list_names = []
    for name in product_files:
        parts = name.split('_')[1]
        if len(parts) > 1:
            list_names.append(parts[1])

    return set(list_names)

#get_scan_number(product_files)
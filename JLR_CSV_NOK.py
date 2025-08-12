import csv , os


def GetFailInfo(file,spath):
    if file.endswith('.csv'):
        file_path = os.path.join(spath, file)
        with open(file_path, 'r') as f:
            reader = csv.reader(f)
            first_row = next(reader)
            fail_idx = first_row.index('testResult')
            test_date = first_row.index('startTestTime')

            # total_rows = sum(1 for _ in reader)  # counts all rows withou the header
            lists = []


            for row in reader:  
                sn = row[0]
                if row[fail_idx] == 'FAIL':
                    list_elem = []
                    list_elem.extend([sn, row[test_date]])
                    for idx, element in enumerate(row):
                        if element == 'FAIL' and idx != fail_idx:
                            fail_info = ','.join([row[idx-1] ]+ row[idx + 1:idx + 4])  # Get the previous, current, and next three elements
                            list_elem.append(fail_info)
                else : continue
                #done with the row
                
                # Check for duplicates
                if len(lists) >= 1 and list_elem[0] == lists[-1][0]:
                    lists.remove(lists[-1])  # Remove the duplicate entry
                    lists.append(list_elem)
                else:
                    lists.append(list_elem)
                        
    else:
        print(f"{file} is not a CSV file.")
        return None

    return lists
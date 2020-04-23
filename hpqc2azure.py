import pandas
import sys
from bs4 import BeautifulSoup
import itertools
import csv


def defects(hpqc_csv_file, iteration):
    df = pandas.read_csv(hpqc_csv_file)
    """
    Title
    Changed Date
    Created Date
    Priority
    Severity
    Tag (Detected By,Target Release,Defect Type,Component)
    Repro Steps (=Description)
    State
    Reason
    """
    # Work Item Type
    df['Work Item Type'] = 'Bug'

    # Iteration
    df['Iteration Path'] = iteration

    # Rename
    df.rename(columns={"Summary": "Title", "Modified Date": "Changed Date", "Detected on Date": "Created Date",
                       "Description": "Repro Steps"},
              inplace=True)

    # Priority - replace
    df['Priority'].replace({
        '1-Must Have': 1,
        '2-Should Have': 2,
        '3-Want to Have': 3,
        '4-Nice to Have': 4}, inplace=True)

    # Severity - replace
    df['Severity'].replace({
        '1-Critical': '1 - Critical',
        '2-High': '2 - High',
        '3-Medium': '3 - Medium',
        '4-Low': '4 - Low'}, inplace=True)

    # Description
    df['Repro Steps'] = df['Repro Steps'].str.cat(df[['Comments']], sep='\n ====== COMMENTS ========= \n',
                                                  na_rep='No Comments')
    df['Repro Steps'] = '<pre>' + df['Repro Steps'] + '</pre>'

    # TODO Dates - drop for now
    df['Changed Date'] = pandas.to_datetime(df['Changed Date'])
    df['Changed Date'] = df['Changed Date'].dt.strftime('%m/%d/%Y %I:%M:%S %p')
    df['Created Date'] = pandas.to_datetime(df['Created Date'])
    df['Created Date'] = df['Created Date'].dt.strftime('%m/%d/%Y %I:%M:%S %p')
    df.drop(columns=["Changed Date", "Created Date"], inplace=True)

    # Tags
    df['Tags'] = "from_hpqc"
    # df['Detected By'] = 'hpqc_detected_by=' + df['Detected By']
    df['Target Release'] = 'hpqc_target_release=' + df['Target Release']
    df['Defect Type'] = 'hpqc_defect_Type=' + df['Defect Type']
    df['Component'] = 'hpqc_component=' + df['Component']
    df['Status'] = 'hpqc_status=' + df['Status']
    df['Tags'] = df['Tags'].str.cat(df[['Target Release', 'Defect Type', 'Component', 'Status']],
                                    sep=';', na_rep='')

    # Status
    df.rename(columns={"Status": "System Info"}, inplace=True)

    # Drop columns
    df.drop(
        columns=["Defect ID", "Assigned To", "Project Name", "Comments", "Detected By", "Target Release", "Defect Type",
                 "Component"], inplace=True)

    # write CSV files
    write_csv_file(df, hpqc_csv_file.split('.csv')[0] + "_out_{i}.csv")
    print('bugs_new(%s) is completed.' % hpqc_csv_file)


def defects_update(azure_csv):
    # Expecting columns:
    # ID, Title, Work Item Type, System Info (containing Status)

    df = pandas.read_csv(azure_csv)
    '''
    df['Reason'] = df['System Info'].copy()
    df['Reason'].replace({
        'Closed': 'Fixed and verified',
        'Duplicate': 'Duplicate',
        'Fixed': 'Fixed and verified',
        'New': 'New',
        'Open': 'Investigate',
        'Postponed': 'Deferred',
        'Re-Open': 'Investigate',
        'Ready for Retest': 'Fixed',
        'Ready for Test': 'Fixed',
        'Rejected': 'As Designed'
    }, inplace=True)
    '''

    df['State'] = df['System Info'].copy()
    df['State'].replace({
        'Closed': 'Closed',
        'Duplicate': 'Closed',
        'Fixed': 'Closed',
        'New': 'New',
        'Open': 'Active',
        'Postponed': 'Closed',
        'Re-Open': 'Active',
        'Ready for Retest': 'Resolved',
        'Ready for Test': 'Resolved',
        'Rejected': 'Closed'
    }, inplace=True)

    # Reset columns
    df['System Info'] = ''
    df['Assigned to'] = ''

    # Drop extra columns
    df = df[['ID', 'Title', 'Work Item Type', 'State', 'System Info', 'Assigned to']]

    # write CSV files
    write_csv_file(df, azure_csv.split('.csv')[0] + "_out_{i}.csv")
    print('bugs_update(%s) is completed.' % azure_csv)


def user_stories(hpqc_csv_file, iteration):
    df = pandas.read_csv(hpqc_csv_file)
    """
    Work Item Type = 'User Story'
    Title = Name
    State = Requirement Status
    Tags = Author, Req Type, Target Release, Related Application
    Priority = Priority
    Description = ReqID, Description, Comments
    Value Area = Requirement Type
       
    """
    # Work Item Type
    df['Work Item Type'] = 'User Story'

    # Iteration
    df['Iteration Path'] = iteration

    # Title
    df.rename(columns={"Name": "Title"}, inplace=True)

    # Priority - replace
    df['Priority'].replace({
        '1-Must Have': 1,
        '2-Should Have': 2,
        '3-Want to Have': 3,
        '4-Nice to Have': 4}, inplace=True)

    # Description
    df['Description'] = 'ReqID / CR #=' + df['ReqID / CR #'].astype(str) + '\n'
    df['Description'] = df['Description'].str.cat(df[['Comments']], sep='\n ====== COMMENTS ========= \n',
                                                  na_rep='No Comments')
    df['Description'] = '<pre>' + df['Description'] + '</pre>'

    # Value Area
    df.rename(columns={"Requirement Type": "Value Area"}, inplace=True)
    df['Value Area'].replace({
        'Folder': 'Business',
        'Functional': 'Business',
        'Non-functional': 'Architectural',
        'Undefined': 'Business'},
        inplace=True)

    # Tags
    df['Tags'] = 'from_hpqc'
    # df['Author'] = 'hpqc_Author=' + df['Author']
    df['Req Type'] = 'hpqc_req_type=' + df['Req Type']
    df['Target Release'] = 'hpqc_target_release=' + df['Target Release']
    # df['Related Application'] = 'hpqc_Related_Application=' + df['Related Application']
    df['Requirement Status'] = 'hpqc_status=' + df['Requirement Status']

    df['Tags'] = df['Tags'].str.cat(
        df[['Req Type', 'Target Release', 'Requirement Status']],
        sep=';', na_rep='')

    # State
    df.rename(columns={"Requirement Status": "Acceptance Criteria"}, inplace=True)

    # Drop extra columns
    df = df[['Work Item Type', 'Title', 'Acceptance Criteria', 'Priority', 'Description', 'Value Area', 'Tags',
             'Iteration Path']]

    # write CSV files
    write_csv_file(df, hpqc_csv_file.split('.csv')[0] + "_out_{i}.csv")
    print('user_stories_new(%s) is completed.' % hpqc_csv_file)


def user_stories_update(azure_csv_file):
    # Expecting columns:
    # ID, Title, Work Item Type, Acceptance Criteria (containing Status)

    df = pandas.read_csv(azure_csv_file)

    # State
    df['State'] = df['Acceptance Criteria'].copy()
    df['State'].replace({
        'Requirement Draft': 'New',
        'Requirement Approved': 'Active',
        'Development Assigned': 'Active',
        'Development Complete': 'Closed'},
        inplace=True)

    # Reset columns
    df['Acceptance Criteria'] = ''
    df['Assigned to'] = ''

    # Drop extra columns
    df = df[['ID', 'Title', 'Work Item Type', 'State', 'Acceptance Criteria', 'Assigned to']]

    # write CSV files
    write_csv_file(df, azure_csv_file.split('.csv')[0] + "_out_{i}.csv")
    print('bugs_update(%s) is completed.' % azure_csv_file)


def test_cases(hpqc_html_file, iteration, schema='azure'):
    # Input
    f = open(hpqc_html_file, 'r', encoding='utf-8')
    soup = BeautifulSoup(f.read(), 'html.parser')

    # remove all attributes - easier to debug
    for tag in soup.findAll(True):
        for attr in [attr for attr in tag.attrs]:
            del tag[attr]

    # Output
    if schema == 'hpqc':
        output_file = hpqc_html_file.split('.')[0] + '_' + schema + '.csv'
        fieldnames = ['id', 'name', 'subject', 'type', 'review_status', 'designer',
                      'execution_status', 'description',
                      'design_steps']
    elif schema == 'azure':
        output_file = hpqc_html_file.split('.')[0] + '_' + schema + '.csv'
        fieldnames = ['Work Item Type', 'Title', 'State', 'Tags', 'Description', 'Steps', 'Iteration Path']
    else:
        raise Exception('format expected (hpqc or azure)')

    csv_file = open(output_file, 'w', encoding='utf-8')
    writer = csv.DictWriter(csv_file, lineterminator='\n', fieldnames=fieldnames)
    writer.writeheader()

    # Parse the html file
    # General structure of HPQC test cases document. We'll wrap <h2> and subsequent <h3>
    # h1 - Tests
    # h2 - Test case name
    # h3 - Design steps
    # ...
    # h2 - Test case name
    # h3 - Design steps
    # ...
    # https://stackoverflow.com/questions/32274222/wrap-multiple-tags-with-beautifulsoup
    #
    test_case_counter = 0
    h2s = soup.find_all('h2')
    for el in h2s:
        # print(el)
        els = [i for i in
               itertools.takewhile(lambda x: x.name != el.name, el.next_siblings)]  # All elements before next <h2>
        # els.insert(0, el)  # Add original <h2>
        # for i in els:
        #    print(i)

        try:
            test_id = el.select("span")[4].text
        except IndexError:
            test_id = None  # some headers has no ID

        # header_table - not all have
        if len(els) < 1:
            print('skipping this one -------------------------- ')
            continue  # Skip this test case - it has only header
        table = els[0]
        trs = table.select("tr")
        tds = trs[1].select("td")
        test_name = children_content(tds[1])
        test_subject = children_content(tds[3])
        tds = trs[2].select("td")
        test_type = children_content(tds[1])
        test_review_status = children_content(tds[3])
        tds = trs[3].select("td")
        test_designer = children_content(tds[1])
        test_execution_status = children_content(tds[3])
        test_description = children_content(trs[5])

        # design steps - not all have
        test_design_steps = []
        if len(els) == 5:
            table = els[3]
            trs = list(table.children)
            for i in range(1, len(trs)):  # Skip first tr - header
                tds = list(trs[i].children)
                design_step_name = children_content(tds[0])
                design_step_description = children_content(tds[1])
                design_step_expected = children_content(tds[2])
                test_design_steps.append(
                    {'name': design_step_name, 'description': design_step_description,
                     'expected': design_step_expected})

        test_case_counter += 1

        # Write csv record
        if schema == 'hpqc':
            writer.writerow({
                'id': test_id,
                'name': test_name,
                'subject': test_subject,
                'type': test_type,
                'review_status': test_review_status,
                'designer': test_designer,
                'execution_status': test_execution_status,
                'description': test_description,
                'design_steps': test_design_steps
            })
        elif schema == 'azure':
            description = '<div>'
            if test_id:
                description += '<p>HPQC ID=' + test_id + '</p>'
            description += '<p>HPQC Type=' + test_type + '</p>'
            description += '<p>' + test_description + '</p>'
            description += '</div>'

            design_steps = '<steps id="0" last="%i">' % (len(test_design_steps) + 1)
            for i in range(0, len(test_design_steps)):
                design_steps += '<step id="%i">' % (i + 2)
                design_steps += '<parameterizedString>%s</parameterizedString>' % test_design_steps[
                    i]['description']
                design_steps += '<parameterizedString>%s</parameterizedString>' % test_design_steps[
                    i]['expected']
                design_steps += '<description/></step>'
            design_steps += '</steps>'

            writer.writerow({
                'Work Item Type': 'Test Case',
                'Tags': 'from_hpqc',
                'Title': test_name,
                'State': 'Design',
                'Description': description,
                'Steps': design_steps,
                'Iteration Path': iteration
            })

            print('test case #%i OK ----------------------- ' % test_case_counter)
    print('parse(%s,%s) completed. Output=%s' % (hpqc_html_file, schema, output_file))


def children_content(soup, content=''):
    """
    Extracts text content from passed Soup Element
    :param soup:
    :param content:
    :return: String content of all the children
    """
    for child in soup.children:
        if child.string:
            content += child.string.strip()
        else:
            return children_content(child, content)
    return content


def write_csv_file(df, output_file_name_template, lines=1000):
    chunks = len(df) // lines + 1
    for i in range(chunks):
        df2 = df[i * lines:(i + 1) * lines]
        filename = output_file_name_template.format(i=i + 1)
        df2.to_csv(filename, index=False)


if __name__ == "__main__":
    usage = 'Usage: python hpqc2azure.py <arguments>. Arguments:' \
            '\n\t -method [defects | defects_update | user_stories | user_stories_update | test_cases]' \
            '\n\t -input file' \
            '\n\t -iteration'

    if len(sys.argv) != 4:
        print(usage)
        exit(1)

    if sys.argv[1] == 'defects':
        defects(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'defects_update':
        defects_update(sys.argv[2])
    elif sys.argv[1] == 'user_stories':
        user_stories(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == 'user_stories_update':
        user_stories_update(sys.argv[2])
    elif sys.argv[1] == 'test_cases':
        user_stories(sys.argv[2], sys.argv[3])
    else:
        print(usage)

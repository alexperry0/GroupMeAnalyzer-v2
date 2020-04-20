import xlsxwriter

def create_summary_data_sheet(workbook, users):
    sheet = workbook.add_worksheet('Summary')

    row = 0
    headings = ['name', 'messages_sent', 'likes_given', 'self_likes', 'likes_received', 'words_sent']
    sheet.write_row(row, 0, headings)
    row += 1
    for user in users:
        data = [users[user]['name'], users[user]['messages_sent'], users[user]['likes_given'],
                users[user]['self_likes'],
                users[user]['likes_received'], users[user]['words_sent']]
        sheet.write_row(row, 0, data)
        row += 1


def create_likes_given_and_received_charts(workbook, users):
    for user in users:
        sheet = workbook.add_worksheet('{}'.format(users[user]['name']))

        names_given = []
        likes_given_to_others = []
        for entry in users[user]['likes_by_member'].items():
            names_given.append(users[entry[0]]['name'])
            likes_given_to_others.append(entry[1])

        headings_given = ['Group Member', 'Number of Likes from Other Group Member']
        sheet.write_row('A1', headings_given)
        sheet.write_column('A2', names_given)
        sheet.set_column(0, 0, 20)
        sheet.write_column('B2', likes_given_to_others)
        sheet.set_column(1, 1, 40)

        chart_given = workbook.add_chart({'type': 'pie'})
        chart_given.set_title({'name': 'Likes Given to Other Members'})
        chart_given.set_style(10)
        # [sheetname, first_row, first_col, last_row, last_col].
        chart_given.add_series({
            'name': 'Likes Given Data',
            'categories': ['{}'.format(users[user]['name']), 1, 0, len(names_given), 0],
            'values': ['{}'.format(users[user]['name']), 1, 1, len(likes_given_to_others), 1],
        })

        names_received = []
        likes_received_from_others = []
        for entry in users[user]['shared_likes'].items():
            names_received.append(users[entry[0]]['name'])
            likes_received_from_others.append(entry[1])

        headings_received = ['Group Member', 'Number of Likes Given to Other Group Member']
        sheet.write_row('D1', headings_received)

        sheet.write_column('D2', names_received)
        sheet.set_column(3, 3, 20)
        sheet.write_column('E2', likes_received_from_others)
        sheet.set_column(4, 4, 50)

        chart_received = workbook.add_chart({'type': 'pie'})
        chart_received.set_title({'name': 'Likes Received from Other Members'})
        chart_received.set_style(10)
        chart_received.add_series({
            'name': 'Likes Received Data',
            'categories': ['{}'.format(users[user]['name']), 1, 3, len(names_received), 3],
            'values': ['{}'.format(users[user]['name']), 1, 4, len(likes_received_from_others), 4],
        })

        sheet.insert_chart('G1', chart_given)
        sheet.insert_chart('G16', chart_received)
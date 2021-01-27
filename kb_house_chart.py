
import xlrd

name = input('./WeeklySeriesTables(시계열).xlsx')
wb = xlrd.open_workbook(name)

sheet = wb.sheet_by_index(0)

lookup = {
  'name': 0,
  'website': 1
}

for rownumber in range(1, sheet.nrows):
  print(rownumber)
  row = sheet.row(rownumber)
  name, website = row[lookup['name']].value, row[lookup['website']].value
  print("Name: %s, Website: %s" % (name, website))

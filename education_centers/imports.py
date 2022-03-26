from openpyxl import load_workbook

from .models import EducationCenter, TrainingProgram, Competence, Criterion
from users.models import DisabilityType

def get_sheet(form):
    workbook = load_workbook(form.cleaned_data['import_file'])
    sheet = workbook.active
    return sheet

def cheak_col_match(sheet, fields_names_set):
    i = 0
    col_count = sheet.max_column
    sheet_fields = []
    sheet_col = {}
    if sheet[f"A2"].value is None:
        return [False, 'EmptySheet']
    try:
        for col_header in range(1, col_count+1):
            if sheet.cell(row=1,column=col_header).value is not None:
                sheet_fields.append(sheet.cell(row=1,column=col_header).value)
                sheet_col[col_header] = sheet.cell(row=1,column=col_header).value
        missing_fields = []
        for field in fields_names_set:
            if field not in sheet_fields:
                missing_fields.append(field)
        if len(missing_fields) != 0:
            return [False, 'FieldError', missing_fields]
    except IndexError:
            return [False, 'IndexError']
    return [True, sheet_col]

def slots_import(form):
    try:
        sheet = get_sheet(form)
    except IndexError:
        return [False, 'IndexError']

    fields_names_set = {
        'ЦО', 'Программа', 
        'Компетенция', 'ОВЗ', 'Краткое описание', 
        'Критерий 1', 'Критерий 2', 'Критерий 3', 
        'Критерий 4', 'Критерий 5'
    }

    cheak = cheak_col_match(sheet, fields_names_set)
    if cheak[0] == False:
        return cheak
    
    sheet_dict = load_worksheet_dict_slots(sheet, cheak[1])
    slots = 0
    nf_ed_centers = set()
    for row in range(len(sheet_dict['Программа'])):
        test = load_slot(sheet_dict, row)
        if test[0] == "OK":
            slots += test[2]
        else:
            nf_ed_centers.add(test[1])
    return [slots, nf_ed_centers]
    
def load_worksheet_dict_slots(sheet, fields_names_set):
    row_count = sheet.max_row
    sheet_dict = {}
    for col in fields_names_set:
        sheet_dict[fields_names_set[col]] = []
        for row in range(2, row_count+1): 
            login = sheet[f"B{row}"].value
            if login != None:
                sheet_dict[fields_names_set[col]].append(sheet.cell(row=row,column=col).value)
    return sheet_dict

def load_slot(sheet_dict, row):
    ed_center = EducationCenter.objects.filter(name=sheet_dict["ЦО"][row])
    if len(ed_center) == 0:
        return f"ЦО \"{ed_center}\" не найдено"
    elif len(ed_center) > 1:
        return f"ЦО \"{ed_center}\" имеет дубликаты"
    ed_center = ed_center[0]

    description = sheet_dict["Краткое описание"][row]

    program = sheet_dict["Программа"][row]
    if len(TrainingProgram.objects.filter(name=program, education_center=ed_center)) != 0:
        return f"Программа \"{program}\" уже существует"

    competence = Competence.objects.filter(name=sheet_dict["Компетенция"][row])
    if (len(competence) == 0):
        return f"Компетенция \"{competence}\" уже существует"
    competence = competence[0]

    program = TrainingProgram(
        name=program,
        competence=competence,
        description=description,
        education_center=ed_center
    )
    program.save()
    disabilities = sheet_dict["ОВЗ"][row]
    if disabilities is not None:
        for disability in disabilities.split(", "):
            disability = DisabilityType.objects.filter(name=disability)
            if len(disability)==0:
                return f"ОВЗ не найденно"
            program.disability_types.add(disability[0])

    criteria = [sheet_dict["Критерий 1"][row], sheet_dict["Критерий 2"][row], sheet_dict["Критерий 3"][row], sheet_dict["Критерий 4"][row], sheet_dict["Критерий 5"][row]]
    for criterion in criteria:
        if len(Criterion.objects.filter(name=criterion))==0:
            criterion = Criterion(name=criterion)
            criterion.save()
        program.criteria.add(criterion)

    return "OK"
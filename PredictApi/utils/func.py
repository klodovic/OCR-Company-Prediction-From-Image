from model.company import *

def spoji(v):
    val = ''
    for s in v:
        s = s + ' '
        val = val.__add__(s)
    return val

def createCompany(entities):
    company = Company()
    for k, v in entities.items():
        if k =='COMPANY':   
            company.company_name = spoji(v)
        if k =='STREET':
            company.street = spoji(v)
        if k =='CITY':
            company.city = spoji(v).title()
        if k =='COUNTRY':
            company.country = spoji(v)
        if k =='PHONE':
            company.phone = spoji(v)
        if k =='FAX':
            company.fax = spoji(v)
        if k =='CELL_PHONE':
            company.cell_phone = spoji(v)
        if k =='POST_NUMBER':
            company.post_number = spoji(v)
        if k =='EMAIL':
            company.email = spoji(v)
        if k =='WEBSITE':
            company.website = spoji(v)
        if k =='MBS':
            company.mbs = spoji(v)
        if k =='IBAN':
            company.iban = spoji(v).upper()
        if k =='OIB':
            company.oib = spoji(v)
    return company


def json_encoder(company):
    if isinstance(company, Company):
        return{'company_name': company.company_name,
                'street': company.street,
                'street': company.street,
                'city': company.city,
                'country': company.country,
                'phone': company.phone,
                'fax': company.fax,
                'cellphone': company.cell_phone,
                'email': company.email,
                'website': company.website,
                'mbs': company.mbs,
                'iban': company.iban,
                'oib': company.oib,
                }
    raise TypeError(f'Object {Company} is not of type Company.')
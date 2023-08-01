class Company:
    def __init__(self):        
        self.company_name = []
        self.street = []
        self.city = []
        self.country =[]
        self.phone = []
        self.fax = []
        self.cell_phone = []
        self.post_number = []
        self.website = []
        self.email = []
        self.oib = []
        self.mbs = []
        self.iban = []
        
    def __repr__(self) -> str:
        return f"{type(self).__name__}(Name: {self.company_name}, Street: {self.street}, City: {self.city}, Country: {self.country}, Phone_ {self.phone}, Post number: {self.post_number}, Fax: {self.fax}, Cell phone: {self.cell_phone}, Website: {self.website}, Email: {self.email}, OIB: {self.oib}, MBS: {self.mbs}, IBAN: {self.iban})"

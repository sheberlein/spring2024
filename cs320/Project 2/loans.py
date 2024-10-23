import json
from zipfile import ZipFile
from io import TextIOWrapper
import csv

class Applicant:
    def __init__(self, age, race):
        self.age = age
        self.race = set()
        for r in race:
            if r in race_lookup:
                self.race.add(race_lookup[r])
    
    def __repr__(self):
        sorted_race = sorted(self.race)
        return f"Applicant('{self.age}', {sorted_race})"

    def lower_age(self):
        curr_age = self.age.replace(">", "")
        curr_age = curr_age.replace("<", "")
        curr_age = curr_age.split("-")
        return int(curr_age[0])

    def __lt__(self, other):
        return self.age.replace(">", "").replace("<", "") < other.age.replace(">", "").replace("<", "")
         
race_lookup = {
    "1": "American Indian or Alaska Native",
    "2": "Asian",
    "3": "Black or African American",
    "4": "Native Hawaiian or Other Pacific Islander",
    "5": "White",
    "21": "Asian Indian",
    "22": "Chinese",
    "23": "Filipino",
    "24": "Japanese",
    "25": "Korean",
    "26": "Vietnamese",
    "27": "Other Asian",
    "41": "Native Hawaiian",
    "42": "Guamanian or Chamorro",
    "43": "Samoan",
    "44": "Other Pacific Islander"
}

class Loan:
    def __init__(self, values):
        try:
            self.loan_amount = float(values["loan_amount"])
        except ValueError:
            self.loan_amount = float(-1)
        # add lines here
        try:
            self.property_value = float(values["property_value"])
        except ValueError:
            self.property_value = float(-1)
        try:
            self.interest_rate = float(values["interest_rate"])
        except ValueError:
            self.interest_rate = float(-1)
        app_list = []
        races_list1 = []
        races_list1.append(values["applicant_race-1"])
        races_list1.append(values["applicant_race-2"])
        races_list1.append(values["applicant_race-3"])
        races_list1.append(values["applicant_race-4"])
        races_list1.append(values["applicant_race-5"])
        app_list.append(Applicant(values["applicant_age"], races_list1))
        
        if (values["co-applicant_age"] != "9999"):
            races_list2 = []
            races_list2.append(values["co-applicant_race-1"])
            races_list2.append(values["co-applicant_race-2"])
            races_list2.append(values["co-applicant_race-3"])
            races_list2.append(values["co-applicant_race-4"])
            races_list2.append(values["co-applicant_race-5"])
            app_list.append(Applicant(values["co-applicant_age"], races_list2))
        
        self.applicants = app_list
        
    def __str__(self):
        length = len(self.applicants)
        return f"<Loan: {self.interest_rate}% on ${self.property_value} with {length} applicant(s)>"
    
    def __repr__(self):
        length = len(self.applicants)
        return f"<Loan: {self.interest_rate}% on ${self.property_value} with {length} applicant(s)>"

    def yearly_amounts(self, yearly_payment):
        # TODO: assert interest and amount are positive
        #result = []
        amt = self.loan_amount
        assert(self.interest_rate > 0)
        assert(amt > 0)

        while amt > 0:
            yield amt
            #result.append(amt)
            # TODO: add interest rate multiplied by amt to amt
            amt += amt * (self.interest_rate / 100)
            # TODO: subtract yearly payment from amt
            amt -= yearly_payment
        #return result
        
        
class Bank:
    def __init__(self, bank):
        with open("banks.json", "r") as f:
            loaded_banks = json.load(f)
        tracker = 0
        for b in loaded_banks:
            if b["name"] == bank:
                self.lei = str(b["lei"])
                tracker = 1
                break
        if tracker == 0:
            raise ValueError("Name not in json file!")
            
    def load_from_zip(self, path):
        listy = []
        with ZipFile(path) as zf:
            with zf.open("wi.csv", "r") as f:
                tio = TextIOWrapper(f)
                reader = csv.DictReader(tio)
                for row in reader:
                    if row["lei"] == self.lei:
                        listy.append(Loan(row))
        self.loanlist = listy
       
    def __getitem__(self, index):
        return self.loanlist[index]
    
    def __len__(self):
        return len(self.loanlist)
    
    def average_interest_rate(self):
        total = 0
        amount = 0
        for loan in self.loanlist:
            try:
                total += loan.interest_rate
                amount += 1
            except ValueError:
                continue
        return total / amount
    
    def num_applicants(self):
        total = 0
        for loan in self.loanlist:
            total += len(loan.applicants)
        return total
    
    def ages_dict(self):
        dicty = {}
        for loan in self.loanlist:
            for applicant in loan.applicants:
                if applicant.age not in dicty:
                    dicty[applicant.age] = 1
                else:
                    dicty[applicant.age] += 1
        return dict(sorted(dicty.items()))

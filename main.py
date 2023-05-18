from gmail import credentialSetup, readGmail, draftGmail
from model import model
import pandas as pd

if __name__ == '__main__':
    cred = credentialSetup()
    df = readGmail(cred, 1)
    first_row = df.iloc[0]
    # cont = model.fit(first_row['content'])
    cont = "This is the body"
    draftGmail(cred, content=cont, recipient=first_row['from'], sender=first_row['to'], subject="RE: "+first_row['subject'])
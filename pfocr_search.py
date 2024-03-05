from Bio import Entrez
Entrez.email = "lagillenwater@gmail.com"

# handle = Entrez.efetch(db = "pubmed", id = "31911834", retmode = "xml")
handle = Entrez.efetch(db = "pubmed", id = "31911834", rettype= "abstract", retmode = "text")
# # records = Entrez.read(handle)
# #keywords =  records['PubmedArticle'][0]['MedlineCitation']['KeywordList'][0]
# handle.close()


# # Open a file for writing
with open('31911834.txt', 'w', encoding='utf-8') as output_file:
    output_file.write(handle.read())
    # # Write the content of the TextIOWrapper object to the file
    # for key in keywords:
    #     output_file.write(str(key) + '\n')


print("Content written")






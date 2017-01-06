import requests, sys
import pprint

'''
Find the most significant phenotype associated with coffe consuption
'''

server = "http://rest.ensembl.org"
phenotype_endpoint = "/phenotype/term/homo_sapiens/{}?"

def fetch_json(server, request):
    """
    Fetch an endpoint from the server and return the decoded JSON results.
    """
    r = requests.get(server+request, headers={ "Content-Type" : "application/json"})

    if not r.ok:
        r.raise_for_status()
        sys.exit()

    return r.json()

if __name__ == "__main__":

    # Find all the phenotypes associated with coffee consuption
    phenotypes = fetch_json(server, phenotype_endpoint.format('coffee consumption'))

    '''
    Find the phenotype with the highest significance
    ie. the lowest p-value (close enough for this example)
    '''
    lowest_seen = 1
    significant_phenotype = None
    for phenotype in phenotypes:
        p_value = float(phenotype['attributes']['p_value'])
        if p_value < lowest_seen:
            lowest_seen = p_value
            significant_phenotype = phenotype

    # Error checking, if we found a phenotype, tell us about it
    if significant_phenotype:
        print "The most significant phenotype is {}\n".format(significant_phenotype['Variation'])
        print "p-value: {}\nrisk allele: {}\nassociated gene(s): {}\nexternal reference: {}\n".format(
            significant_phenotype['attributes']['p_value'],
            significant_phenotype['attributes']['risk_allele'],
            significant_phenotype['attributes']['associated_gene'],
            significant_phenotype['attributes']['external_reference'])

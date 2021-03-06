import requests, sys
import pprint

'''
Use the VEP to find the consequences of the variant
'''

server = "http://rest.ensembl.org"
phenotype_endpoint = "/phenotype/term/homo_sapiens/{}?"
variation_endpoint = "/variation/human/{}?content-type=application/json&pops=1"
populations = "/info/variation/populations/homo_sapiens?content-type=application/json;filter=LD"
vep = "/vep/human/region/{}/T?content-type=application/json"

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

        # Remember the value for later, just to make the variable names more readable
        risk_allele = significant_phenotype['attributes']['risk_allele']
    else:
        # If we don't find any phenotypes, we're doing something wrong
        print "We didn't find a phenotype? This is bad."
        sys.exit()

    '''
    Now that we have the most significant phenotype, fetch the record for this variation.
    Also get the populations and make a dictionary based on the population short name
    '''
    varition_data = fetch_json(server, variation_endpoint.format(significant_phenotype['Variation']))
    populations = fetch_json(server, populations);
    population_lookup = { p['name']: p for p in populations }

    # Tell us about any mappings to the genome we've found for this variation
    if varition_data['mappings']:
        print "Variant mappings found"
        for mapping in varition_data['mappings']:
            print "Assembly: {}\nLocation: {}\nallele_string: {}".format(
                mapping['assembly_name'],
                mapping['location'],
                mapping['allele_string'])

            # Use the VEP to find the consequences of a variation at this location
            vep_results = fetch_json(server, vep.format(mapping['location']))
            for vep in vep_results:
                print "The consequences are: {}".format(vep['most_severe_consequence'])

            print

    '''
    Filter the population data in this variant for
    - 1000 Genomes data
    - Alleles matching the risk allele
    - Populations in the list of populations we have LD data for
    '''
    pops = varition_data['populations']
    filtered_pops = (p for p in pops if p['population'].startswith('1000GENOMES') and \
                     p['allele'] == risk_allele and \
                     p['population'] in population_lookup)

    # Find the top 3 populations and tell us about them, including the full description
    # for the population
    for pop in sorted( filtered_pops, key=lambda x: x['frequency'], reverse=True)[:3]:

        population = pop['population']
        print "Population: {} ({})".format(population_lookup[population]['description'], pop['population'])
        print "With a frequency of {}".format(pop['frequency'])
        print "And allel count of {}\n".format(pop['allele_count'])

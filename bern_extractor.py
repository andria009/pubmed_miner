# -*- coding: utf-8 -*-
"""bern_extractor.py
extracting Named Entity Recognition using BioBert from PubMed documents, with BERN project service API @Korea University

usage: bern_extractor.py -i <inputfile> -o <outputfile>
"""

import json
import requests
import sys
import getopt
import os
from tqdm import tqdm

verbose = False

def parse_arguments(argv):
  inputfile = ''
  outputfile = ''

  if (len(argv)) == 0:
    usage()
    sys.exit(2)
  else:
    try:
      opts, args = getopt.getopt(argv, 'hvi:o:', ['help', 'verbose','ifile=', 'ofile='])
    except getopt.GetoptError as err:
      print(err)
      usage()
      sys.exit(2)

    verbose = False;
    for opt, arg in opts:
      if opt in ('-h', '--help'):
        usage()
        sys.exit()
      elif opt in ('-v', '--verbose'):
        verbose = True
      elif opt in ('-i', '--ifile'):
        inputfile = arg
      elif opt in ('-o', '--ofile'):
        outputfile = arg
      else:
        assert False, 'unhandled option'

    extract_biobert(verbose, inputfile, outputfile)

def usage():
  print('bern_extractor.py -i <inputfile> -o <outputfile>')
  print('options:')
  print('   -h, --help       show this help message and exit')
  print('   -v, --verbose    set verbose')
  print('   -i, --ifile      give input file name')
  print('   -o, --ofile      set output file name')

def extract_biobert(vb, inpF, outF):

  with open(inpF, 'r') as inp:
    print('PubMed Ids: ' + inpF)
    print('Output    : ' + outF)

    for pmId in tqdm(inp.readlines()):

      bern_out = requests.get('https://bern.korea.ac.kr/pubmed/' + pmId)
      bern_data = bern_out.json()

      diseases = []
      genes = []
      drugs = []
      specieses = []
      mutations = []
      diseases_list = []
      genes_list = []
      drugs_list = []
      specieses_list = []
      mutations_list = []
      for bern_item in bern_data:
        if ('sourcedb' in bern_item and 'sourceid' in bern_item):
          id = bern_item['sourcedb'] + bern_item['sourceid']
        else:
          break

        if 'text' in bern_item:
          text = bern_item['text']
        else:
          break

        if 'logits' in bern_item:
          if 'disease' in bern_item['logits']:
            diseases = bern_item['logits']['disease']
          if 'gene' in bern_item['logits']:
            genes = bern_item['logits']['gene']
          if 'drug' in bern_item['logits']:
            drugs = bern_item['logits']['drug']
          if 'species' in bern_item['logits']:
            specieses = bern_item['logits']['species']
          if 'mutation' in bern_item['logits']:
            mutations = bern_item['logits']['mutation']

          for disease in diseases:
            start = disease[0]['start']
            end = disease[0]['end']

            disease_str = text[start:end]

            if (disease_str not in diseases_list):
              diseases_list.append(disease_str)

          for gene in genes:
            start = gene[0]['start']
            end = gene[0]['end']

            gene_str = text[start:end]

            if (gene_str not in genes_list):
              genes_list.append(gene_str)

          for drug in drugs:
            start = drug[0]['start']
            end = drug[0]['end']

            drug_str = text[start:end]

            if (drug_str not in drugs_list):
              drugs_list.append(drug_str)

          for species in specieses:
            start = species[0]['start']
            end = species[0]['end']

            species_str = text[start:end]

            if (species_str not in specieses_list):
              specieses_list.append(species_str)

          for mutation in mutations:
            start = mutation[0]['start']
            end = mutation[0]['end']

            mutation_str = text[start:end]

            if (mutation_str not in mutations_list):
              mutations_list.append(mutation_str)

          out = {
            "id": id,
            "text": text,
            "diseases": diseases_list,
            "genes": genes_list,
            "drugs": drugs_list,
            "species": specieses_list,
            "mutations": mutations_list
          }

          json_out = json.dumps(out)

        else:
          break

        with open(outF, 'a') as out:
          out.write(json_out + os.linesep)

if __name__ == "__main__":
  parse_arguments(sys.argv[1:])
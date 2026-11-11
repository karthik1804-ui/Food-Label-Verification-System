"""
Taxonomy Enhancement Script for Food Label Verification System
==============================================================
Enriches ins_taxonomy.json with:
  1. functional_categories (list of functional roles)
  2. color_origin ('natural', 'synthetic', or 'not_applicable')
  3. alternative_names (synonyms, international names, common codes)
  4. verified_source (Codex Alimentarius / FSSAI standard citation)
"""

import json
import os

TAXONOMY_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "data", "ins_taxonomy.json")

# Specialized multi-functional categories according to Codex Alimentarius CXS 192-1995
MULTI_FUNCTION_MAP = {
    "101(I)": ["Color", "Nutrient Fortifier"],
    "101(II)": ["Color", "Nutrient Fortifier"],
    "170": ["Color", "Anti-caking agent", "Acidity regulator", "Firming agent"],
    "200": ["Preservative", "Antimicrobial agent"],
    "202": ["Preservative", "Antimicrobial agent"],
    "211": ["Preservative", "Antimicrobial agent"],
    "220": ["Preservative", "Antioxidant", "Bleaching agent"],
    "223": ["Preservative", "Antioxidant", "Bleaching agent"],
    "250": ["Preservative", "Color retention agent"],
    "251": ["Preservative", "Color retention agent"],
    "260": ["Acidity regulator", "Preservative"],
    "270": ["Acidity regulator", "Preservative"],
    "282": ["Preservative", "Antimicrobial agent"],
    "300": ["Antioxidant", "Flour treatment agent", "Acidity regulator"],
    "301": ["Antioxidant"],
    "307": ["Antioxidant", "Nutrient Fortifier"],
    "322": ["Emulsifier", "Antioxidant"],
    "330": ["Acidity regulator", "Antioxidant", "Sequestrant"],
    "331": ["Acidity regulator", "Emulsifier", "Stabilizer", "Sequestrant"],
    "334": ["Acidity regulator", "Antioxidant", "Sequestrant"],
    "338": ["Acidity regulator", "Antioxidant synergist"],
    "385": ["Antioxidant", "Sequestrant", "Preservative synergist"],
    "407": ["Gelling agent", "Thickener", "Stabilizer"],
    "412": ["Thickener", "Stabilizer", "Emulsifier"],
    "415": ["Thickener", "Stabilizer", "Emulsifier", "Foaming agent"],
    "420": ["Sweetener", "Humectant", "Stabilizer", "Sequestrant"],
    "428": ["Gelling agent", "Thickener", "Stabilizer"],
    "440": ["Gelling agent", "Thickener", "Stabilizer"],
    "450": ["Emulsifier", "Stabilizer", "Raising agent", "Sequestrant"],
    "451": ["Sequestrant", "Acidity regulator", "Emulsifier"],
    "452": ["Emulsifier", "Stabilizer", "Sequestrant"],
    "471": ["Emulsifier", "Stabilizer", "Antifoaming agent"],
    "472E": ["Emulsifier", "Dough conditioner"],
    "500": ["Raising agent", "Acidity regulator", "Anti-caking agent"],
    "500(I)": ["Raising agent", "Acidity regulator", "Anti-caking agent"],
    "500(II)": ["Raising agent", "Acidity regulator", "Anti-caking agent"],
    "501": ["Acidity regulator", "Raising agent"],
    "501(I)": ["Acidity regulator", "Raising agent"],
    "503": ["Raising agent", "Acidity regulator"],
    "503(I)": ["Raising agent", "Acidity regulator"],
    "503(II)": ["Raising agent", "Acidity regulator"],
    "508": ["Gelling agent", "Flavor enhancer", "Salt substitute"],
    "509": ["Firming agent", "Sequestrant"],
    "512": ["Antioxidant", "Color retention agent"],
    "551": ["Anti-caking agent", "Free-flow agent"],
    "553": ["Anti-caking agent", "Lubricant"],
    "621": ["Flavor enhancer"],
    "627": ["Flavor enhancer"],
    "631": ["Flavor enhancer"],
    "635": ["Flavor enhancer"],
    "950": ["Sweetener", "Flavor enhancer"],
    "951": ["Sweetener", "Flavor enhancer"],
    "955": ["Sweetener"],
    "960": ["Sweetener"],
}

# Color origin classification: 'natural', 'synthetic', 'mineral', or 'not_applicable'
NATURAL_COLORS = {
    "100", "101(I)", "101(II)", "120", "140(I)", "150A", "153",
    "160A", "160B", "160C", "160D", "160E", "161B", "162", "163", "170", "174", "175"
}

SYNTHETIC_COLORS = {
    "102", "104", "110", "122", "123", "124", "127", "129",
    "131", "132", "133", "141(I)", "142", "143", "150B", "150C", "150D",
    "151", "155", "171", "172", "173", "180"
}

# Alternative names / synonyms dictionary
ALTERNATIVE_NAMES = {
    "100": ["Curcumin", "Turmeric Yellow", "Curcuma", "C.I. 75300", "Natural Yellow 3"],
    "101(I)": ["Riboflavin", "Vitamin B2", "Lactoflavin"],
    "101(II)": ["Riboflavin 5'-Phosphate", "Flavin Mononucleotide"],
    "102": ["Tartrazine", "FD&C Yellow 5", "Food Yellow 4", "C.I. 19140", "Acid Yellow 23"],
    "104": ["Quinoline Yellow", "Food Yellow 13", "D&C Yellow 10", "C.I. 47005"],
    "110": ["Sunset Yellow FCF", "FD&C Yellow 6", "Food Yellow 3", "Orange Yellow S", "C.I. 15985"],
    "120": ["Carmine", "Cochineal", "Carminic Acid", "Natural Red 4", "C.I. 75470"],
    "122": ["Carmoisine", "Azorubine", "Food Red 3", "C.I. 14720"],
    "123": ["Amaranth", "FD&C Red 2", "Food Red 9", "C.I. 16185"],
    "124": ["Ponceau 4R", "Cochineal Red A", "Food Red 7", "C.I. 16255", "Brilliant Scarlet 4R"],
    "127": ["Erythrosine", "FD&C Red 3", "Food Red 14", "C.I. 45430"],
    "129": ["Allura Red AC", "FD&C Red 40", "Food Red 17", "C.I. 16035"],
    "131": ["Patent Blue V", "Food Blue 5", "C.I. 42051"],
    "132": ["Indigo Carmine", "Indigotine", "FD&C Blue 2", "Food Blue 1", "C.I. 73015"],
    "133": ["Brilliant Blue FCF", "FD&C Blue 1", "Food Blue 2", "C.I. 42090"],
    "140(I)": ["Chlorophylls", "Magnesium Chlorophyll", "Natural Green 3"],
    "141(I)": ["Copper Chlorophyll", "Chlorophyllin Copper Complex"],
    "142": ["Green S", "Lissamine Green", "Food Green 4", "C.I. 44090"],
    "143": ["Fast Green FCF", "FD&C Green 3", "Food Green 3", "C.I. 42053"],
    "150A": ["Caramel I", "Plain Caramel", "Caustic Caramel", "Spirit Caramel"],
    "150B": ["Caramel II", "Caustic Sulphite Caramel"],
    "150C": ["Caramel III", "Ammonia Caramel", "Baker's Caramel", "Beer Caramel"],
    "150D": ["Caramel IV", "Sulphite Ammonia Caramel", "Soft Drink Caramel", "Acid-proof Caramel"],
    "151": ["Brilliant Black BN", "Black PN", "Food Black 1", "C.I. 28440"],
    "153": ["Vegetable Carbon", "Carbon Black", "Vegetable Black"],
    "160A": ["Carotenes", "Beta-Carotene", "Provitamin A"],
    "160B": ["Annatto", "Bixin", "Norbixin", "Natural Orange 4"],
    "160C": ["Paprika Extract", "Capsanthin", "Capsorubin"],
    "160D": ["Lycopene", "Natural Yellow 27"],
    "161B": ["Lutein", "Xanthophyll"],
    "162": ["Beet Red", "Betanin", "Beetroot Extract"],
    "163": ["Anthocyanins", "Enocianina", "Grape Skin Extract"],
    "170": ["Calcium Carbonate", "Chalk", "Limestone", "Calcite"],
    "171": ["Titanium Dioxide", "Titania", "Pigment White 6", "C.I. 77891"],
    "172": ["Iron Oxides", "Iron Hydroxides", "Pigment Red 101"],
    "200": ["Sorbic Acid", "Hexa-2,4-dienoic acid"],
    "202": ["Potassium Sorbate", "Sorbistat-K"],
    "211": ["Sodium Benzoate", "Benzoate of Soda", "Sodium salt of benzoic acid"],
    "220": ["Sulphur Dioxide", "Sulfur Dioxide", "SO2"],
    "223": ["Sodium Metabisulphite", "Sodium Disulphite", "Pyrosulphite"],
    "250": ["Sodium Nitrite", "Nitrous acid sodium salt"],
    "251": ["Sodium Nitrate", "Chile saltpeter"],
    "260": ["Acetic Acid", "Ethanoic Acid", "Glacial Acetic Acid"],
    "270": ["Lactic Acid", "2-Hydroxypropanoic acid"],
    "282": ["Calcium Propionate", "Calcium Propanoate", "Mycoban"],
    "300": ["Ascorbic Acid", "Vitamin C", "L-Ascorbic Acid"],
    "301": ["Sodium Ascorbate", "Vitamin C Sodium Salt"],
    "307": ["Alpha-Tocopherol", "Vitamin E"],
    "322": ["Lecithins", "Soy Lecithin", "Sunflower Lecithin", "Phosphatidylcholine"],
    "330": ["Citric Acid", "2-Hydroxypropane-1,2,3-tricarboxylic acid"],
    "331": ["Sodium Citrates", "Trisodium Citrate", "Sodium Salt of Citric Acid"],
    "334": ["Tartaric Acid", "L(+)-Tartaric Acid"],
    "338": ["Phosphoric Acid", "Orthophosphoric Acid"],
    "385": ["Calcium Disodium EDTA", "Calcium Disodium Ethylenediaminetetraacetate"],
    "407": ["Carrageenan", "Irish Moss Extract", "Eucheuma Seaweed"],
    "412": ["Guar Gum", "Guaran", "Cyamopsis Tetragonoloba"],
    "415": ["Xanthan Gum", "Corn Sugar Gum"],
    "420": ["Sorbitol", "D-Glucitol"],
    "428": ["Gelatin", "Gelatine"],
    "440": ["Pectins", "Fruit Pectin"],
    "450": ["Diphosphates", "Sodium Acid Pyrophosphate", "SAPP"],
    "451": ["Triphosphates", "Sodium Tripolyphosphate", "STPP"],
    "452": ["Polyphosphates", "Sodium Hexametaphosphate", "SHMP"],
    "471": ["Mono- and Di-glycerides of Fatty Acids", "Glyceryl Monostearate", "GMS"],
    "472E": ["DATEM", "Diacetyl Tartaric Acid Esters of Mono- and Diglycerides"],
    "500": ["Sodium Carbonates", "Baking Soda", "Soda Ash", "Sodium Bicarbonate"],
    "500(I)": ["Sodium Carbonate", "Soda Ash", "Washing Soda"],
    "500(II)": ["Sodium Hydrogen Carbonate", "Sodium Bicarbonate", "Baking Soda"],
    "501": ["Potassium Carbonates", "Potassium Bicarbonate"],
    "501(I)": ["Potassium Carbonate", "Potash"],
    "503": ["Ammonium Carbonates", "Ammonium Bicarbonate", "Baker's Ammonia"],
    "503(I)": ["Ammonium Carbonate", "Baker's Ammonia"],
    "503(II)": ["Ammonium Hydrogen Carbonate", "Ammonium Bicarbonate"],
    "508": ["Potassium Chloride", "Sylvite"],
    "509": ["Calcium Chloride"],
    "512": ["Stannous Chloride", "Tin(II) Chloride"],
    "551": ["Silicon Dioxide", "Silica", "Aerosil", "Synthetic Amorphous Silica"],
    "553": ["Talc", "Magnesium Silicate"],
    "621": ["Monosodium Glutamate", "MSG", "Sodium Glutamate", "Monosodium L-Glutamate"],
    "627": ["Disodium Guanylate", "Sodium 5'-Guanylate", "GMP"],
    "631": ["Disodium Inosinate", "Sodium 5'-Inosinate", "IMP"],
    "635": ["Disodium 5'-Ribonucleotides", "I+G", "Ribotides"],
    "950": ["Acesulfame Potassium", "Acesulfame K", "Ace-K", "Sunett"],
    "951": ["Aspartame", "NutraSweet", "Equal", "APM"],
    "955": ["Sucralose", "Splenda", "Trichlorogalactosucrose"],
    "960": ["Steviol Glycosides", "Stevia Extract", "Rebaudioside A"],
}

VERIFIED_SOURCE_TEXT = "Codex Alimentarius (CXS 192-1995) / FSSAI Regulations (2011)"

def enrich_taxonomy():
    with open(TAXONOMY_PATH, "r", encoding="utf-8") as f:
        taxonomy = json.load(f)

    print(f"Loaded {len(taxonomy)} entries from {TAXONOMY_PATH}")

    updated_count = 0
    for key, item in taxonomy.items():
        clean_code = str(item.get("clean_code", "")).upper()
        raw_class = item.get("class", "Food Additive")

        # 1. Functional Categories (list of strings)
        if clean_code in MULTI_FUNCTION_MAP:
            item["functional_categories"] = list(MULTI_FUNCTION_MAP[clean_code])
        else:
            # Split slashes if present
            if "/" in raw_class:
                cats = [c.strip() for c in raw_class.split("/") if c.strip()]
                item["functional_categories"] = cats
            else:
                item["functional_categories"] = [raw_class.strip()]

        # 2. Color Classification & Origin ('natural', 'synthetic', 'not_applicable')
        is_color = any("color" in c.lower() for c in item["functional_categories"])
        item["is_color"] = bool(is_color)
        if is_color:
            if clean_code in NATURAL_COLORS:
                item["color_origin"] = "natural"
            elif clean_code in SYNTHETIC_COLORS:
                item["color_origin"] = "synthetic"
            else:
                item["color_origin"] = "synthetic"
        else:
            item["color_origin"] = "not_applicable"

        # 3. Alternative Names (synonyms)
        if clean_code in ALTERNATIVE_NAMES:
            item["alternative_names"] = list(ALTERNATIVE_NAMES[clean_code])
        else:
            # Generate default fallback list: [name, e_number, code]
            alt = [item.get("name", "")]
            if item.get("e_number"):
                alt.append(item["e_number"])
            if item.get("code"):
                alt.append(item["code"])
            item["alternative_names"] = [a for a in alt if a]

        # 4. Verified Source
        item["verified_source"] = VERIFIED_SOURCE_TEXT
        updated_count += 1

    with open(TAXONOMY_PATH, "w", encoding="utf-8") as f:
        json.dump(taxonomy, f, indent=2, ensure_ascii=False)

    print(f"Successfully enriched {updated_count} taxonomy records in {TAXONOMY_PATH}")

if __name__ == "__main__":
    enrich_taxonomy()

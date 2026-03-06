import os

output_file = 'CLAUDE_ONBOARDING_MEGA_V45.md'

files_to_include = [
    ('DOME_COSMOLOGY_MASTER_V45.md', 'markdown', 'CORE FRAMEWORK & ONBOARDING'),
    ('v45_pipeline.py', 'python', 'V45 PIPELINE SOURCE CODE (Math & Derivations)'),
    ('v41_dome_engine.html', 'html', 'V41 3D DOME ENGINE (Coordinates & Visualization)'),
    ('v45_master_results.csv', 'csv', 'V45 MASTER SCORECARD DATA'),
    ('v45_predictions.csv', 'csv', 'V45 NEW PREDICTIONS DATA'),
    ('v42_saa_separation.csv', 'csv', 'V42 SAA SEPARATION DATA'),
    ('v43_predictions.csv', 'csv', 'V43 PREDICTIONS DATA'),
    ('v44_master_results.csv', 'csv', 'V44 MASTER RESULTS DATA'),
]

with open(output_file, 'w', encoding='utf-8') as outfile:
    outfile.write("# MEGA-ONBOARDING DOCUMENT FOR CLAUDE: DOME COSMOLOGY V45\n\n")
    outfile.write("This document contains the complete context, theoretical framework, mathematical derivations, source code, 3D visualization engine, and resulting data tables for the Dome Cosmology model up to Version 45. You now have 100% of the available context.\n\n")
    outfile.write("---\n\n")
    
    for filename, lang, title in files_to_include:
        if os.path.exists(filename):
            outfile.write(f"## {title} (`{filename}`)\n\n")
            outfile.write(f"```{lang}\n")
            with open(filename, 'r', encoding='utf-8') as infile:
                content = infile.read()
                outfile.write(content)
                if not content.endswith('\n'):
                    outfile.write("\n")
            outfile.write("```\n\n---\n\n")
        else:
            outfile.write(f"## {title}\n*(File `{filename}` not found)*\n\n---\n\n")

print(f"Successfully built {output_file}")

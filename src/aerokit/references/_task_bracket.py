"""References for the 2026 final-challenge work on the bracket task (owned by one parallel session; add entries here only)."""
from aerokit.references import Reference

REFERENCES: tuple[Reference, ...] = (
    Reference("ansys_structural_steel_ed231", "Ansys Inc. (export); ansys/pymaterials-manager test data", 2022,
              "Engineering Data 23.1.0.209 export 'Structural Steel' (steel_eglass_air.xml)",
              "GitHub ansys/pymaterials-manager, tests/data", url="https://raw.githubusercontent.com/ansys/"
              "pymaterials-manager/main/tests/data/steel_eglass_air.xml",
              note="local copy read 2026-11-04: rho 7850, E 200 GPa, nu 0.3, Fty 250 MPa, Ftu 460 MPa, CTE 1.2e-5/C, "
                   "k 60.5, cp 434, S-N (ASME VIII-2 Table 5-110.1); MatML layout used by aerokit.bracket.cards"),
    Reference("en_1993_1_2_2005", "CEN", 2005, "Eurocode 3: Design of steel structures — Part 1-2: General rules — "
              "Structural fire design (EN 1993-1-2:2005)", "European Committee for Standardization",
              url="https://www.phd.eng.br/wp-content/uploads/2015/12/en.1993.1.2.2005.pdf",
              note="Table 3.1 at 300 C: k_y 1.000, k_p 0.613, k_E 0.800 (read from the page image by a sub-agent "
                   "2026-11-04; the text layer is shifted)"),
    Reference("baumers_2010", "M. Baumers, C. Tuck, R. Hague, I. Ashcroft, R. Wildman", 2010,
              "A comparative study of metallic additive manufacturing power consumption",
              "Proc. 21st Solid Freeform Fabrication Symposium, Austin TX, pp. 278-288",
              url="https://utw10945.utweb.utexas.edu/Manuscripts/2010/2010-25-Baumers.pdf",
              note="Table 5: SLM250 316L 31 kWh/kg, Arcam A1 Ti-6Al-4V 17 kWh/kg (sub-agent read 2026-11-04)"),
    Reference("kellens_2017", "K. Kellens, M. Baumers, T. G. Gutowski, W. Flanagan, R. Lifset, J. R. Duflou", 2017,
              "Environmental dimensions of additive manufacturing: mapping application domains and their "
              "environmental implications", "Procedia CIRP 61:582-587", url="https://lirias.kuleuven.be/retrieve/450931",
              note="Table 2 atomisation 7.02-31.7 MJ/kg; Table 4 SLM 83-588 MJ/kg; Table 8 kerosene 12.5 t/(100 kg y) "
                   "short haul, 103 t long haul, 25 y (sub-agent read 2026-11-04)"),
    Reference("carter_2014", "W. T. Carter, M. W. Erno, D. H. Abbott, C. E. Bruck, G. H. Wilson, J. B. Wolfe, "
              "D. M. Finkhousen, A. Tomasella, R. A. Jensen", 2014,
              "The GE aircraft engine bracket challenge: an experiment in crowdsourcing for mechanical design concepts",
              "Proc. 25th Solid Freeform Fabrication Symposium, pp. 1402-1411",
              url="https://utw10945.utweb.utexas.edu/sites/default/files/2014-110-Carter.pdf",
              note="Fig. 2 loads 8000 lbf up, 8500 lbf out, 9500 lbf at 42 deg, 5000 lbf in torsion; Ti-6Al-4V "
                   "(sub-agent read 2026-11-04). Original mass: '1.8 kg' here vs 2033 g in the GE press release"),
    Reference("ashby_2013_env", "M. F. Ashby", 2013, "Materials and the Environment: Eco-informed Material Choice",
              "Butterworth-Heinemann", edition="2nd",
              note="family values read through the 'Useful numbers for environmental studies' reproduction "
                   "(useful_numbers_env); low-carbon steel 25-28 MJ/kg, 1.8 kg CO2/kg (pp. 463-469)"),
)

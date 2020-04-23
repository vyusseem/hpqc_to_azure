# hpqc_to_azure
Utility to convert HPQC data (defects, requirements, test cases) to Azure DevOps

# Defects CSV input file structure:
 - Defect ID
 - Summary
 - Description
 - Comments
 - Status
 - Severity
 - Priority
 - Assigned To
 - Detected By
 - Project Name
 - Target Release
 - Defect Type
 - Component
 - Modified Date
 - Detected on Date 
 
# Requirements (User Stories) CSV input file structure:
 - ReqID / CR #
 - Name
 - Description
 - Author
 - Creation Date
 - Requirement Status
 - Requirement Type
 - Target Release
 - Req Type
 - Priority
 - Modified Date
 - Comments
 - Assigned To
 - Related Application
 
# Test case (with Design steps)
html file from HPQC can be converted automatically.

 # Usage Example
 `python.py defects from_hpqc.csv iteration_1` 
 
 Azure DevOps compatible `from_hpqc_out.csv` will be generated beside input file.
 
 
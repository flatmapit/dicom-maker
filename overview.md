Project problem statement

I want a *native* python CLI application, that does not rely on other external tools, that will create synthetic dicom and send it to a specified host, port and with configurable AEC/AET.

Research whether there is already a good tool to do this. 

I would like to be able to create study/series/image counts like https://github.com/flatmapit/dicom-fabricator does, based on configs or command lines.

The tool should be able to create studies locally according to my specification, and I should be able to view details of those studies from the CLI, and send those local studies to a PACS with C-STORE (after verifying the connection details with C-ECHO).


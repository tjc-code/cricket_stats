This is a small Python project to scrape [cricinfo](https://www.espncricinfo.com/) to get player data and check how England men's batters averages have changed as a result of Stokes and McCullum's leadership. 

Run
```
python get_bazzball_average_changes.py
```

Output (on 11/03/24)

 player      | Stokes_ave | not_stokes_ave | increase 
 ----------- | ---------- | -------------- | -------- 
 Z Crawley   | 36.59      | 27.81          | 8.78     
 BM Duckett  | 46.68      | 15.71          | 30.97    
 OJ Pope     | 37.97      | 29.65          | 8.32     
 JE Root     | 52.77      | 49.2           | 3.57     
 HC Brook    | 62.15      | nan            | nan      
 JM Bairstow | 45.96      | 34.54          | 11.42    
 BA Stokes   | 34.46      | 35.77          | -1.31    
 BT Foakes   | 30.14      | 28.11          | 2.03     

Stokes has increased average of batters per innings by:  63.8

for x in range(result.start, result.end):
          
        #     line = linecache.getline(result.filename, x)
        #     print(f'line is {line}')
        #     pattern = r'^[\s]*(def)\s[a-zA-Z0-9\_]*\([a-zA-Z0-9\_\,\s\=\[\]\(\)\{\}\*\&\%\!\-\"\'\+\;\.]*\)(\s\:|\:)[\n]*[\s]*(""")'
            
        #     match = re.search(pattern,line)
        #     print(f'match is {match}') 
        #     # try:
        #     #  if match:
        #     # #   print(f'match is {match}')   
        #     #   print(f'outer match is {match.group()}')
        #     # except:
        #     #     print(f'no match')

        #     if match and (self.config.get("open") in line):
        #         # print(f'match is {match.group()}')
        #         returned = True 
        #         print(f' Returned value if match is matched is {returned}')
        #         break
                
        #     else:
        #         returned = False
        #         print(f'Returned value if match not matched {returned}')
        #     # if self.config.get("open") in line:
        #     #     returned = True
        #     #     break
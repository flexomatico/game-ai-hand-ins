result = {}
result['UP'] = 0.1
result['DOWN'] = 32
result['RIGHT'] = -0.3
result['LEFT'] = -20

print(max(result, key=result.get))
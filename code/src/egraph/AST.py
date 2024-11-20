from collections import deque
import re

class Node():
    left = ''
    key = ''
    right = ''

def process(input):
    arr = [c for c in input]
    i = 0
    first = ''
    stack = deque()
    print(arr)
    
    while i < len(arr):
        
        if arr[i] == '(':

            if not stack:
                k = Node()
                stack.append(k)
                first = k
            else:
                
                s = stack[-1]
                k = Node()
                if s.left == '' and s.right == '':
                    s.left = k
                elif s.left ==  '':
                    s.left = k
                else:
                    s.right = k
                stack.append(k)
                
        elif arr[i] == ')':    
            stack.pop()

        elif re.search("[0-9]+", arr[i]):
            s = stack[-1]

            if s.left == '' and s.right == '':
                k = Node()
                k.key = arr[i]
                s.left = k
                
            elif s.left ==  '':
                k = Node()
                k.key = arr[i]
                s.left = k
             
            else:
                k = Node()
                k.key = arr[i]
                s.right = k
         
        elif arr[i] == '/' or arr[i] == '*':
            s = stack[-1]
            s.key = arr[i]

        elif arr[i] == ' ':
            pass

        else:
            s = stack[-1]

            if s.left == '' and s.right == '':
                k = Node()
                k.key = arr[i]
                s.left = k
            elif s.left ==  '':
                k = Node()
                k.key = arr[i]
                s.left = k
            else:
                k = Node()
                k.key = arr[i]
                s.right = k

        i += 1

    return first

def preorder(node):
    
    if node.left == '' and node.right == '':
        print(node.key)
        print(' ')
        return
    else:
        print(node.key)
    preorder(node.left)
    preorder(node.right)

first = process("(/ (* a 2) 2)") 


preorder(first)
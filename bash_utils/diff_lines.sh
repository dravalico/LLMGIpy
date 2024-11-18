#!/bin/bash

# This .sh takes a file 1 and a file 2 as inputs. It provides a file 3 which have the lines that are in file 1 but not in file 2.

grep -v -F -x -f ${2} ${1} > ${3}


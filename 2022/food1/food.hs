import Data.Text (Text, splitOn, pack)
import Data.Text.Read (decimal)
import Data.List

-- Parse the input file containg blocks of numbers separated by double newlines:
-- "1000\n2000\n3000\n\n4000\n\n..." becomes a list of lists [["1000","2000","3000"], ["4000"], ...]
-- Does not handle extra newlines at the end and beginning of the input file
parse :: Text -> [[Text]]
parse txt = map (splitOn (pack "\n")) (splitOn (pack "\n\n") txt)

-- Returns undefined if the conversion fails
textToInt :: Text -> Int
textToInt txt = case decimal txt of
         Right (a, _) -> a
         Left _ -> undefined

textsToInts :: [[Text]] -> [[Int]]
textsToInts xss = [map textToInt xs | xs <- xss]

-- Calculate the sum of the integers in each block and
-- part1: find the highest number
-- part2: calculate the sum of the three highest numbers
main :: IO ()
main = do
  contents <- readFile "big.in"
  let xss = reverse (sort (map sum (textsToInts (parse (pack contents))))) in
    do
      print("part1", head xss)              -- get the highest number
      print("part2", sum (take 3 xss))      -- calculate the sum of the three highest numbers



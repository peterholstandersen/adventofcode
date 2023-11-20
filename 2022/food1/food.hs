import Data.Text (Text, splitOn, pack)
import Data.Text.Read (decimal)
import Data.List

-- does not handle extra newlines at the end and beginning of the input file
parse :: Text -> [[Text]]
parse txt = map (splitOn (pack "\n")) (splitOn (pack "\n\n") txt)

textToInt :: Text -> Int
textToInt txt = case decimal txt of
         Right (a, _) -> a
         Left _ -> undefined

textsToInts :: [[Text]] -> [[Int]]
textsToInts xss = [map textToInt xs | xs <- xss]

main :: IO ()
main = do
  contents <- readFile "big.in"
  let xss = reverse (sort (map sum (textsToInts (parse (pack contents))))) in
    do
      print("part1", head xss)
      print("part2", sum (take 3 xss))



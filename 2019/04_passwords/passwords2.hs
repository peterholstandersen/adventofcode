import Data.Text (Text, splitOn, pack)
import Data.Text.Read (decimal)
import Data.List

-- count the number of adjacent digits anywhere
-- advance until we reach the digit and count from there
countAdjacent :: Char -> String -> Int
countAdjacent x [] = 0
countAdjacent x xs =
  if x /= head xs
  then countAdjacent x (tail xs)
  else 1 + countAdjacent1 x (tail xs)

countAdjacent1 :: Char -> String -> Int
countAdjacent1 _ [] = 0
countAdjacent1 x xs =
  if x == head xs
  then 1 + countAdjacent1 x (tail xs)
  else 0

-- true if there are any double digits (double = 2 or more adjacent)
anyDoubleDigits :: String -> Bool
anyDoubleDigits xs = any (\x -> countAdjacent x xs >= 2) ['1'..'9']

-- true if there are any digits doubles, which are not triple or more
anyExactlyDoubleDigits :: String -> Bool
anyExactlyDoubleDigits xs = any (\x -> countAdjacent x xs == 2) ['1'..'9']


-- generate all passwords between low and high where the digits in the number
-- does not decrease, e.g., 1234, 1457, 7777, 7778, 7788. Not: 1121, 1197
passwords :: String -> String -> [String]
passwords low high = filter (\x -> low <= x && x <= high) $ passwords1 low high

passwords1 :: String -> String -> [String]
passwords1 [x] [y] = [ [a] | a <- [x..y] ]
passwords1 xs ys   = [ a ++ [b]
                     | a <- passwords1 (init xs) (init ys)
                     , b <- [(last a)..'9']
                     ]


-- part1: count the number of passwords (numbers) in range 152085 670283 that
-- . is a six-digit number.
-- . two adjacent digits are the same (like 22 in 122345).
-- . going from left to right, the digits never decrease; they only ever increase or stay the same (like 111123 or 135679).

-- part2: count the number of passwords (numbers) in range 152085 670283 that
-- . as part1, only the two adjacent digits may not be part of larger group
-- . 112345 is ok: 11 qualifies
-- . 111345 is ok: 111 does not qualify (most be exactly 2 adjacent digits)
-- . 111335 is ok: 111 does not qualify, but 33 does

test :: IO ()
test = do
  print("part1", length $ filter anyDoubleDigits $ passwords "152085" "670283")        -- 1764
  print("part2", length $ filter anyExactlyDoubleDigits $ passwords "152085" "670283") -- 1196

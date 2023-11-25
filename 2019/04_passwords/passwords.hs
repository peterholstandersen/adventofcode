import Data.Text (Text, splitOn, pack)
import Data.Text.Read (decimal)
import Data.List

-- Ints as lists. Why? Why not?
-- Elements in the lists are 1..9 inclusive
-- 0 represents the empty list
--
-- 123 corresponds to the list [3,2,1] in reverse
-- so  headInt 123 = 123 mod 10 = 3    ... head [3,2,1] = 3
-- and tailInt 123 = 123 div 10 = 12   ... tail [3,1,1] = [2,1]
--
-- consInt 4 123 = 123*10 + 4 = 1234   ... cons 4 [3,2,1] = [4,3,2,1]
consInt :: Int -> Int -> Int
consInt x xs = x * 10 + xs

tailInt :: Int -> Int
tailInt 0 = undefined
tailInt xs = xs `div` 10

headInt :: Int -> Int
headInt 0 = undefined
headInt xs = xs `mod` 10

-- count the number of adjacent digits anywhere in a number
-- advance in the "list" until we reach the digit and count from there
countAdjacent :: Int -> Int -> Int
countAdjacent x 0 = 0
countAdjacent x xs =
  if x /= headInt xs
  then countAdjacent x (tailInt xs)
  else 1 + countAdjacent1 x (tailInt xs)

countAdjacent1 :: Int -> Int -> Int
countAdjacent1 _ 0 = 0
countAdjacent1 x xs =
  if x == headInt xs
  then 1 + countAdjacent1 x (tailInt xs)
  else 0

-- true if there are any double digits in the number (double = 2 or more adjacent)
anyDoubleDigits :: Int -> Bool
anyDoubleDigits xs = any (\x -> countAdjacent x xs >= 2) [1..9]

-- true if there are any digits doubles, that are not triple or more
anyExactlyDoubleDigits :: Int -> Bool
anyExactlyDoubleDigits xs = any (\x -> countAdjacent x xs == 2) [1..9]


-- generate all passwords between low and high where the digits in the number
-- does not decrease, e.g., 1234, 1457, 7777, 7778, 7788. Not: 1121, 1197
passwords :: Int -> Int -> [Int]
passwords low high = filter (\x -> low <= x && x <= high) $ passwords1 low high

passwords1 :: Int -> Int -> [Int]
passwords1 xs ys
  | xs == 0 || ys == 0 = []
  | xs < 10 && ys < 10 = [ a | a <- [xs..ys] ]
  | otherwise          = [ consInt a b
                         | a <- passwords1 (tailInt xs) (tailInt ys)
                         , b <- [(headInt a)..9]
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
  print("part1", length $ filter anyDoubleDigits $ passwords 152085 670283)        -- 1764
  print("part2", length $ filter anyExactlyDoubleDigits $ passwords 152085 670283) -- 1196

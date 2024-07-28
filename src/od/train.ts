// DONE 将句子排序 https://leetcode.cn/problems/sorting-the-sentence/
function sortSentence(s: string): string {
	const arr = s.split(' ')
	arr.sort((a, b) => {
		return a[a.length - 1] > b[b.length - 1] ? 1 : -1
	})
	return arr.map(item => item.slice(0, -1)).join(' ')
}

// DONE 字符串压缩 https://leetcode-cn.com/problems/compress-string-lcci/
function compressString(S: string) {
	let result = ''
	let last = ''
	let count = 1
	for (let i of S) {
		if (last === '') last = i
		else if (last === i) count++
		else {
			result = result + last + count
			last = i
			count = 1
		}
	}
	result = result + last + count
	if (result.length < S.length) return result
	else return S
}

// DONE 括号匹配 https://leetcode-cn.com/problems/valid-parentheses/
function isValid(s: string): boolean {
	const stack: string[] = []
	for (let i of s) {
		switch (i) {
			case '(':
				stack.push(')')
				break
			case '[':
				stack.push(']')
				break
			case '{':
				stack.push('}')
				break
			default:
				if (stack.pop() !== i) return false
		}
	}
	return stack.length === 0
}
// DONE 输出金字塔
function printPyramid(n: number) {
	for (let i = 1; i <= n; i++) {
		let str = ''
		for (let j = 1; j <= n - i; j++) {
			str += ' '
		}
		for (let j = 1; j <= 2 * i - 1; j++) {
			str += '*'
		}
		console.log(str)
	}
}

// DONE 字符串交换 https://leetcode.cn/problems/check-if-one-string-swap-can-make-strings-equal/description/
function areAlmostEqual(s1: string, s2: string): boolean {
	let diff: number[] = []
	for (let i = 0; i < s1.length; i++) {
		if (s1[i] !== s2[i]) {
			if (diff.length > 2) return false
			diff.push(i)
		}
	}
	if (diff.length === 0) return true
	if (diff.length !== 2) return false
	return s1[diff[0]] === s2[diff[1]] && s1[diff[1]] === s2[diff[0]]
}

// DONE 盛水最多的容器 https://leetcode.cn/problems/container-with-most-water/description/
function maxArea(height: number[]): number {
	let area = 0
	let left = 0
	let right = height.length - 1
	while (left < right) {
		area = Math.max(
			area,
			(right - left) * Math.min(height[left], height[right])
		)
		height[left] < height[right] ? left++ : right--
	}
	return area
}
// DONE 反转单词中元音字母 https://leetcode.cn/problems/reverse-vowels-of-a-string/description/
function reverseVowels(s: string): string {
	const arr: string[] = []
	const vowels = 'aeiouAEIOU'.split('')
	let result = ''
	for (let i of s) {
		if (vowels.includes(i)) {
			arr.push(i)
		}
	}
	for (let i of s.split('')) {
		if (vowels.includes(i)) {
			result += arr.pop()
		} else result += i
	}
	return result
}
// DONE 反转每对括号间的子串 https://leetcode-cn.com/problems/reverse-substrings-between-each-pair-of-parentheses/
function reverseParentheses(s: string): string {
	let ans = s
	let reverse = (s: string) => {
		return s.split('').reverse().join('') //反转字符串
	}
	let match = [] //用一个数组作为括号的栈
	for (let i = 0; i < s.length; i++) {
		if (s[i] == '(') {
			match.push(i + 1) //入栈 存储一个左括号的位置
		} else if (s[i] == ')') {
			let m = match.pop() //出栈 取出一个左括号的位置
			ans =
				ans.substring(0, m) +
				reverse(ans.substring(m || 0, i)) +
				ans.substring(i, ans.length) //反转指定的部分
		}
	}
	return ans.replaceAll('(', '').replaceAll(')', '') //最后去除字符串里的括号
}

// DONE 字符串之和 https://leetcode.cn/problems/calculate-digit-sum-of-a-string/description/
function digitSum(s: string, k: number): string {
	if (s.length <= k) {
		return s
	}
	let count = 0
	let str = ''
	for (let i = 0; i < s.length; i++) {
		count += Number(s[i])
		if ((i + 1) % k === 0) {
			str += count.toString()
			count = 0
		}
	}
	if (s.length % k) {
		str += count
	}
	return digitSum(str, k)
}

// TODO 快递运输

// TODO 兑换零钱 https://leetcode.cn/problems/gaM7Ch/
function coinChange(coins: number[], amount: number): number {
	let dp: number[] = new Array(amount + 1).fill(Infinity)
	dp[0] = 0
	for (let i = 1; i <= amount; i++) {
		for (let j = 0; j < coins.length; j++) {
			if (i - coins[j] >= 0) dp[i] = Math.min(dp[i], dp[i - coins[j]] + 1)
		}
	}
	return dp[amount] == Infinity ? -1 : dp[amount]
}

// TODO 所有不相同的排列数 https://leetcode.cn/problems/permutations/description/
// 给定一个只包含大写英文字母的字符串S，要求你给出对S重新排列的所有不相同的排列数。
// 如：S为ABA，则不同的排列有ABA、AAB、BAA三种
function permutation(S: string) {
	let result = new Set<string>()
	let arr = S.split('')
	let dfs = (path: string, arr: string[]) => {
		if (arr.length === 0) {
			result.add(path)
			return
		}
		for (let i = 0; i < arr.length; i++) {
			dfs(
				path + arr[i],
				arr.filter((item, index) => index !== i)
			)
		}
	}
	dfs('', arr)
	return result.size
}

// TODO 回文

// TODO 输出最长子串的长度 https://leetcode.cn/problems/longest-substring-without-repeating-characters/
function lengthOfLongestSubstring(s: string): number {
	if (s.length === 1) return 1
	let result = 0
	for (let i = s.length; i > 0; i--) {
		for (let j = 0; j <= s.length - i; j++) {
			if (isHasDouble(s.slice(j, j + i))) {
				result = i
				return result
			}
		}
	}
	return result
}
function isHasDouble(s: string) {
	return Array.from(new Set(s.split(''))).length === s.length
}

// TODO 给定一个任意长度的数组，找出其中加起来之和为 24 的所有组合

console.log(lengthOfLongestSubstring('au'))

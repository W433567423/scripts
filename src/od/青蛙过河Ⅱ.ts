// TODO 青蛙过河Ⅱ
function maxJump(stones: number[]): number {
	let result = 0
	// 一次跳俩，要回头
	for (let i = 2; i < stones.length; i++) {
		result = Math.max(result, stones[i] - stones[i - 2])
	}
	return result
}

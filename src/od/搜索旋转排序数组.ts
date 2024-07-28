console.clear()
// TODO 搜索旋转排序数组
function f(nums: number[], target: number) {
	if (!nums.length) return -1

	let left = 0
	let right = nums.length - 1
	while (left <= right) {
		let temp = (left + right) >> 1
		if (nums[temp] === target) {
			return temp
		}
		if (nums[temp] < nums[right]) {
			if (nums[temp] < target && target <= nums[right]) {
				left = temp + 1
			} else {
				// 不在
				right = temp - 1
			}
		} else {
			if (nums[temp] <= target && target < nums[temp]) {
				right = temp - 1
			} else {
				left = temp + 1
			}
		}
	}
	return -1
}

console.log(f([4, 5, 6, 7, 0, 1, 2], 0))
console.log(f([4, 5, 6, 7, 0, 1, 2], 4))

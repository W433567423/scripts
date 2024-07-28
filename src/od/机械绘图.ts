// 机械绘图/计算面积
import readline from 'readline'

const rl = readline.createInterface({
	input: process.stdin,
	output: process.stdout
})

rl.question('', line1 => {
	const [n, e] = line1.split(' ').map(x => parseInt(x))
	let lastX = 0 // 记录上一个位置的横坐标
	let y = 0 // 记录起始点的纵坐标
	let area = 0 // 记录面积
	let count = n
	rl.on('line', line => {
		const [x, d] = line.split(' ').map(x => parseInt(x))
		area += (x - lastX) * Math.abs(y) // 计算执行第i个指令后的增量面积
		y += d // 更新纵坐标
		lastX = x // 更新上一个位置的横坐标
		if (--count === 0) {
			area += (e - lastX) * Math.abs(y) // 计算终点的增量面积
			console.log(area)
			rl.close()
		}
	})
})

import fs from 'fs'
import path from 'path'
const main = () => {
	console.clear()
	// 获取 C:\Users\t4335\Desktop\牛客网-算法基础入门+算法基础提升+算法中级+算法高级 - 带源码课件 目录下所有文件夹
	const dir1 =
		'C:/Users/t4335/Desktop/牛客网-算法基础入门+算法基础提升+算法中级+算法高级 - 带源码课件'
	const files1 = fs.readdirSync(dir1)

	for (const file1 of files1) {
		if (file1[0] === '0') {
			const dir2 = path.join(dir1, file1)
			const files2 = fs.readdirSync(dir2)
			for (const file2 of files2) {
				// 如果不是文件夹则跳过
				if (!fs.statSync(path.join(dir2, file2)).isDirectory()) {
					continue
				}
				const dir3 = path.join(dir2, file2)
				console.log(dir3)
				const files3 = fs.readdirSync(dir3)
				// 将dir3下的所有文件移动到dir2下
				if (files3.length === 0) {
					console.log('🚀 ~ main ~ dir3:', dir3)

					fs.existsSync(dir3) && fs.rmdirSync(dir3)
				} else if (files3.length === 1) {
					fs.renameSync(
						path.join(dir3, files3[0]),
						path.join(dir2, dir3.split('\\').pop() + '.mp4')
					)
				} else {
					for (const file3 of files3) {
						fs.renameSync(
							path.join(dir3, file3),
							path.join(dir2, `${file3.slice(0, file3.lastIndexOf('.'))}.mp4`)
						)
					}
				}
			}
		}
	}
}

main()

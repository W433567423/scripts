// 智能成绩表
const readline = require('readline')
const rl = readline.createInterface({
	input: process.stdin,
	output: process.stdout
})
class Student {
	name: string
	totalScore: number
	scores: Record<string, number>
	constructor(name: string) {
		this.name = name
		this.totalScore = 0
		this.scores = {}
	}
	addScore(subject: string, score: number) {
		this.scores[subject] = score
		this.totalScore += score
	}
	getScore(subject: string) {
		return this.scores[subject] || 0
	}
}
async function processInput() {
	// 通过 readline 逐行读取输入
	const lines = []
	for await (const line of rl) {
		lines.push(line)
	}
	// 解析输入数据
	const [n, m] = lines[0].split(' ').map(Number)
	const subjects = lines[1].split(' ')
	const students = []
	// 读取每个学生的姓名和成绩
	for (let i = 0; i < n; i++) {
		const tokens = lines[i + 2].split(' ')
		const student = new Student(tokens[0])
		for (let j = 0; j < m; j++) {
			student.addScore(subjects[j], parseInt(tokens[j + 1], 10))
		}
		students.push(student)
	}
	const rankSubject = lines[n + 2]
	students.sort((s1, s2) => {
		const score1 = rankSubject === '' ? s1.totalScore : s1.getScore(rankSubject)
		const score2 = rankSubject === '' ? s2.totalScore : s2.getScore(rankSubject)
		if (score1 !== score2) {
			return score2 - score1
		} else {
			return s1.name.localeCompare(s2.name)
		}
	})

	students.forEach(student => process.stdout.write(`${student.name} `))
	process.stdout.write('\n')
	rl.close()
}
processInput()

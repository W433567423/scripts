import axios from 'axios'
import dayjs from 'dayjs'

// sleep 函数
const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms))

// 设置想查询的红包个数
const len = 80

const main = async () => {
	console.warn(`[!]正在查询历史最新${len}个点券红包的数据...\n`)
	// 保存所有红包数据列表
	let r: any[] = []
	try {
		for (let i = 1; i <= len / 20; i++) {
			const { data } = await axios.get(
				'https://api.unipay.qq.com/v1/r/1450043395/red_envelope_service',
				{
					params: {
						from_h5: 1,
						t: dayjs().valueOf(),
						openid: '2C93F8F2F15D387488DB09F3CA5D0B8B',
						appid: 1450019044,
						action: 'get_grab_list_info',
						page_size: 20,
						page_num: i,
						encrypt_msg:
							'df4f73749ff4325eb9f899769280abac29fefda6250d5ed8113a0b2dea190c3c1603e78b8b24db14a522dd840344bed83c2ba7e11f3ef840057ccf7a0f941e6e32d9b7d8b77058f52bb78a709debe1e131137759a5276911279136a0a141c6bde6982a6b383e1cb998661455244b20b775b270e1f8d9a6b0083b7895d1a4d267',
						activity_id: 'Activity_1638352102_GGLQBG'
					}
				}
			)

			const draw_list = data.data.draw_list
			r = r.concat(draw_list)
			console.warn(
				`[!]成功发送第${i}次请求，当前已获取${r.length}个点券红包数据...`
			)
			await sleep(1000)
		}
	} catch {
		console.warn(`[!]查询失败，请检查网络连接`)
		return
	}

	// 根据 draw_amount、exchange_status 分类，并计数
	const m = new Map()
	r.forEach(e => {
		let key = `${e.draw_amount.padEnd(5)}点券-${
			e.exchange_status ? '已使用' : '未使用'
		}`
		if (m.has(key)) {
			m.set(key, Number(m.get(key).split('个')[0]) + 1 + '个')
		} else {
			m.set(key, '1个')
		}
	})

	// 展示
	const startTime = dayjs(Number(r[r.length - 1].draw_time + '000')).format(
		'YYYY-MM-DD HH:mm:ss'
	)
	const endTime = dayjs(Number(r[0].draw_time + '000')).format(
		'YYYY-MM-DD HH:mm:ss'
	)
	const noUseList = r.filter(e => e.exchange_status === 0)
	const lastTime = dayjs(
		Number(noUseList[noUseList.length - 1].draw_time + '000')
	).format('YYYY-MM-DD HH:mm:ss')
	console.warn()
	console.warn(`[!]从${startTime}到${endTime}`)
	console.warn(`[!]王者荣耀点券红包分类统计:`)
	console.log(m)
	console.warn(`[!]当前未使用的点券红包总个数为:${noUseList.length}`)
	console.warn(`[!]最早未使用的点券红包与${lastTime}领取`)
}
main()

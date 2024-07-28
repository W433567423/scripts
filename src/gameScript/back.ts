//获取红包的接口
const getURL = (page_num: number) => {
	return `
	https://api.unipay.qq.com/v1/r/1450043395/red_envelope_service?from_https=1&from_h5=1&pf=mds_wechat_qb-html5-html5&pfkey=pfkey&accounttype=qb&t=1713813974419&scene=&sandbox=&offerId=1450043395&openid=2C93F8F2F15D387488DB09F3CA5D0B8B&openkey=4F699CD1CECCB0F577CCF9840E1873D1&session_id=openid&session_type=kp_accesstoken&qq_appid=101502376&wx_appid=wx951bdcac522929b6&accountType=qq&appid=1450019044&activity_id=Activity_1638352102_GGLQBG&model_id=&action=get_grab_list_info&page_size=20&page_num=${page_num}&encrypt_msg=df4f73749ff4325eb9f899769280abac29fefda6250d5ed8113a0b2dea190c3c1603e78b8b24db14a522dd840344bed83c2ba7e11f3ef840057ccf7a0f941e6e32d9b7d8b77058f52bb78a709debe1e131137759a5276911279136a0a141c6bde6982a6b383e1cb998661455244b20b775b270e1f8d9a6b0083b7895d1a4d267&msg_len=126
`
}

// const { data } = await axios.get(getURL(i))
// pf: null,
// scene: null,
// sandbox: null,
// 'mds_wechat_qb-html5-html5': null,
// model_id: null
// from_https: 1,
// pfkey: 'pfkey',
// accounttype: 'qb',
// offerId: 1450043395,
// openkey: '4F699CD1CECCB0F577CCF9840E1873D1',
// session_id: 'openid',
// session_type: 'kp_accesstoken',
// qq_appid: 101502376,
// wx_appid: 'wx951bdcac522929b6',
// accountType: 'qq',
// appid: 1450019044,
// msg_len: 126

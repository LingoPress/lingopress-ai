from sentence_transformers import SentenceTransformer, util

model1 = SentenceTransformer('sentence-transformers/paraphrase-MiniLM-L3-v2')
model2 = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model3 = SentenceTransformer('jhgan/ko-sroberta-multitask')

sentences = ["모라에스는 좌파였던 적이 없으며, 이전에도 사회민주당(PSDB), 노동자당(PT)에 소속되어있었다. 그리고 상파울루의 공공 보안 부서과 테메르의에 장관직으로 일하였다.",
             "모라에스는 전통적인 야당인 브라질 사회민주당(PSDB)과 노동자당(PT) 소속으로 상파울루의 공안부 장관과 테메르의 장관으로 일한 적이 있는 좌파가 아니었습니다."]
sentences2 = ["그들 중 일부를 리포스팅하는 동안, 머스크는 모라에스에게 “그의 범죄들에 대해 심판 받아야해“라고 말했다.",
              "머스크는 이 중 일부를 다시 게시하면서 모라에스는 \"그의 범죄에 대해 재판을 받아야 한다\"고 말했습니다."]

embedding_1 = model1.encode(sentences[0], convert_to_tensor=True)
embedding_2 = model1.encode(sentences[1], convert_to_tensor=True)

print(util.pytorch_cos_sim(embedding_1, embedding_2))
print(util.dot_score(embedding_1, embedding_2))

embedding_1 = model2.encode(sentences[0], convert_to_tensor=True)
embedding_2 = model2.encode(sentences[1], convert_to_tensor=True)

print(util.pytorch_cos_sim(embedding_1, embedding_2))
print(util.dot_score(embedding_1, embedding_2))

embedding_1 = model3.encode(sentences[0], convert_to_tensor=True)
embedding_2 = model3.encode(sentences[1], convert_to_tensor=True)

print(util.pytorch_cos_sim(embedding_1, embedding_2))
print(util.dot_score(embedding_1, embedding_2))

print("")

embedding_1 = model1.encode(sentences2[0], convert_to_tensor=True)
embedding_2 = model1.encode(sentences2[1], convert_to_tensor=True)

print(util.pytorch_cos_sim(embedding_1, embedding_2))
print(util.dot_score(embedding_1, embedding_2))

embedding_1 = model2.encode(sentences2[0], convert_to_tensor=True)
embedding_2 = model2.encode(sentences2[1], convert_to_tensor=True)

print(util.pytorch_cos_sim(embedding_1, embedding_2))
print(util.dot_score(embedding_1, embedding_2))

embedding_1 = model3.encode(sentences2[0], convert_to_tensor=True)
embedding_2 = model3.encode(sentences2[1], convert_to_tensor=True)

print(util.pytorch_cos_sim(embedding_1, embedding_2))
print(util.dot_score(embedding_1, embedding_2))



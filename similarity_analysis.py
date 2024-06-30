from sentence_transformers import SentenceTransformer, util


class SimilarityAnalysis:
    def __init__(self):
        #model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        #model = SentenceTransformer('jhgan/ko-sroberta-multitask')
        model = SentenceTransformer('./model_all-MiniLM-L6-v2')

        self.model = model

    def get_similarity(self, query, passage):
        print(query, passage)
        query_embedding = self.model.encode(query)
        passage_embedding = self.model.encode(passage)
        similarity = util.pytorch_cos_sim(query_embedding, passage_embedding)
        print(similarity.item())
        return f"{similarity.item():.4f}"

# query_embedding = model.encode("그들 중 일부를 리포스팅하는 동안, 머스크는 모라에스에게 “그의 범죄들에 대해 심판 받아야해“라고 말했다.")
# passage_embedding = model.encode("머스크는 이 중 일부를 다시 게시하면서 모라에스는 \"그의 범죄에 대해 재판을 받아야 한다\"고 말했습니다.")
# similarity = util.dot_score(query_embedding, passage_embedding)

# print(f"{similarity.item():.4f}")
